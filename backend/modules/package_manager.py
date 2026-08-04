import os
import shutil
import subprocess
import urllib.parse
import urllib.request
import re
import json


class PackageManagerModule:

    managers_data = {
        "winget": (
            "WinGet",
            "winget",
            "Windows Package Manager"
        ),
        "choco": (
            "Chocolatey",
            "choco",
            "Windows package manager"
        ),
        "pip": (
            "pip",
            "pip",
            "Python package installer"
        ),
        "npm": (
            "npm",
            "npm",
            "Node package manager"
        ),
    }

    def managers(self):
        return [
            {
                "id": k,
                "name": n,
                "command": c,
                "description": d,
                "installed": shutil.which(c) is not None
            }
            for k, (n, c, d) in self.managers_data.items()
        ]

    def installed_software(self):
        if not shutil.which("winget"):
            return {
                "source": None,
                "available": False,
                "output": "",
                "message": "WinGet is not available."
            }

        try:
            p = subprocess.run(
                [
                    "winget",
                    "list",
                    "--accept-source-agreements"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "source": "winget",
                "available": p.returncode == 0,
                "output": p.stdout,
                "error": p.stderr
            }

        except (OSError, subprocess.SubprocessError) as e:
            return {
                "source": "winget",
                "available": False,
                "output": "",
                "error": str(e)
            }

    def search_pypi(self, query):
        url = "https://pypi.org/simple/"

        try:
            request = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/vnd.pypi.simple.v1+json",
                    "User-Agent": "Modular-WebApp/1.0"
                }
            )

            with urllib.request.urlopen(
                request,
                timeout=30
            ) as response:

                data = response.read().decode("utf-8")

            projects = json.loads(data).get("projects", [])
            query_lower = query.strip().lower()

            matches = [
                project["name"]
                for project in projects
                if query_lower in project["name"].lower()
            ]

            matches.sort(
                key=lambda name: (
                    name.lower() != query_lower,
                    not name.lower().startswith(query_lower),
                    len(name),
                    name.lower()
                )
            )

            results = [
                {
                    "name": name,
                    "description": "PyPI package"
                }
                for name in matches[:50]
            ]

            return {
                "manager": "pip",
                "query": query,
                "available": True,
                "results": results
            }

        except Exception as e:
            return {
                "manager": "pip",
                "query": query,
                "available": True,
                "results": [],
                "error": str(e)
            }

    def search(self, manager_id, query):

        if manager_id not in self.managers_data:
            return {
                "error": "Unknown package manager"
            }

        if not query.strip():
            return {
                "manager": manager_id,
                "results": []
            }

        if manager_id == "pip":
            return self.search_pypi(query)

        name, cmd, _ = self.managers_data[manager_id]

        if os.name == "nt" and manager_id == "npm":
            cmd = "npm.cmd"

        if not shutil.which(cmd):
            return {
                "manager": manager_id,
                "available": False,
                "message": f"{name} is not available on PATH."
            }

        args = {
            "winget": [
                cmd,
                "search",
                query,
                "--accept-source-agreements"
            ],
            "choco": [
                cmd,
                "search",
                query,
                "--limit-output"
            ],
            "npm": [
                cmd,
                "search",
                query,
                "--json"
            ]
        }[manager_id]

        try:
            p = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "manager": manager_id,
                "query": query,
                "available": True,
                "returncode": p.returncode,
                "output": p.stdout,
                "error": p.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                "manager": manager_id,
                "query": query,
                "available": True,
                "error": "Search timed out."
            }

        except OSError as e:
            return {
                "manager": manager_id,
                "query": query,
                "available": True,
                "error": str(e)
            }

    # ---------------------------------------------------------
    # DOWNLOADS
    # ---------------------------------------------------------

    def get_download_directory(self):
        downloads = os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            "MODULAR"
        )

        os.makedirs(downloads, exist_ok=True)

        return downloads

    def download_package(self, manager_id, package_name):

        if manager_id not in self.managers_data:
            return {
                "success": False,
                "manager": manager_id,
                "package": package_name,
                "error": "Unknown package manager."
            }

        if not package_name or not package_name.strip():
            return {
                "success": False,
                "manager": manager_id,
                "package": package_name,
                "error": "Package name is empty."
            }

        package_name = package_name.strip()
        download_dir = self.get_download_directory()

        name, cmd, _ = self.managers_data[manager_id]

        if os.name == "nt" and manager_id == "npm":
            cmd = "npm.cmd"

        if not shutil.which(cmd):
            return {
                "success": False,
                "manager": manager_id,
                "package": package_name,
                "error": f"{name} is not available on PATH."
            }

        if manager_id == "pip":
            args = [
                cmd,
                "download",
                "--dest",
                download_dir,
                package_name
            ]

        elif manager_id == "npm":
            args = [
                cmd,
                "pack",
                package_name,
                "--pack-destination",
                download_dir
            ]

        elif manager_id == "winget":
            args = [
                cmd,
                "download",
                "--id",
                package_name,
                "--download-directory",
                download_dir,
                "--accept-source-agreements"
            ]

        elif manager_id == "choco":
            args = [
                cmd,
                "download",
                package_name,
                "--output-directory",
                download_dir
            ]

        else:
            return {
                "success": False,
                "manager": manager_id,
                "package": package_name,
                "error": "Download is not implemented for this manager."
            }

        try:
            process = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=300
            )

            success = process.returncode == 0

            return {
                "success": success,
                "manager": manager_id,
                "package": package_name,
                "returncode": process.returncode,
                "directory": download_dir,
                "output": process.stdout,
                "error": process.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "manager": manager_id,
                "package": package_name,
                "directory": download_dir,
                "error": "Download timed out after five minutes."
            }

        except OSError as e:
            return {
                "success": False,
                "manager": manager_id,
                "package": package_name,
                "directory": download_dir,
                "error": str(e)
            }

    def download_packages(self, packages):

        results = []

        for package in packages:
            manager = package.get("manager")
            name = package.get("package")

            results.append(
                self.download_package(
                    manager,
                    name
                )
            )

        return {
            "directory": self.get_download_directory(),
            "total": len(results),
            "successful": sum(
                1 for result in results
                if result["success"]
            ),
            "failed": sum(
                1 for result in results
                if not result["success"]
            ),
            "results": results
        }