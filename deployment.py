import requests
import subprocess
import os

class DeploymentManager:
    def __init__(self, github_token, vercel_token):
        self.github_token = github_token
        self.vercel_token = vercel_token

    def create_github_repo(self, repo_name):
        """Membuat repository baru di GitHub."""
        url = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "name": repo_name,
            "private": False
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return response.json()["html_url"]
        else:
            raise Exception(f"Gagal membuat repo GitHub: {response.text}")

    def push_to_github(self, repo_url, local_path):
        """Melakukan push kode lokal ke GitHub."""
        try:
            os.chdir(local_path)
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit by Agentic AI"], check=True)
            subprocess.run(["git", "branch", "-M", "main"], check=True)
            subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
            subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
            return True
        except Exception as e:
            raise Exception(f"Gagal push ke GitHub: {str(e)}")

    def deploy_to_vercel(self, project_path):
        """Mendeploy proyek ke Vercel menggunakan Vercel CLI."""
        try:
            os.chdir(project_path)
            # Menjalankan vercel deploy secara non-interaktif
            result = subprocess.run(
                ["vercel", "--token", self.vercel_token, "--yes", "--prod"],
                capture_output=True, text=True, check=True
            )
            # Mencari URL deployment di output
            for line in result.stdout.split('\n'):
                if "https://" in line and "vercel.app" in line:
                    return line.strip()
            return "Deployment berhasil, silakan cek dashboard Vercel."
        except Exception as e:
            raise Exception(f"Gagal deploy ke Vercel: {str(e)}")
