import asyncio
import aiohttp
import logging
from github3 import login
from github3.exceptions import NotFoundError, UnprocessableEntity
from config.settings import Settings

logger = logging.getLogger("GitHubHandler")

class GitHubHandler:
    def __init__(self):
        self.github = login(token=Settings.GITHUB_TOKEN)
        self.repo = self.github.repository(*Settings.GITHUB_REPO.split('/'))

    async def create_issue(self, task_name: str, description: str) -> int:
        title = f"🚀 {task_name} - AI Task"
        body = f"""### Auto-Generated Task

{description}

_Assigned to AI agents._
"""
        async with aiohttp.ClientSession() as session:
            try:
                for issue in self.repo.issues(state="open"):
                    if issue.title == title:
                        logger.warning(f"⚠️ Issue already exists: {issue.html_url}")
                        return issue.number

                issue = await self.repo.create_issue(title=title, body=body)
                logger.info(f"✅ Created GitHub Issue: {issue.html_url}")
                return issue.number

            except Exception as e:
                logger.error(f"❌ Failed to create or find issue: {e}")
                raise


    async def create_pull_request(self, task_name: str, branch_name: str, issue_number: int) -> int:
        async with aiohttp.ClientSession() as session:
            try:
                default_branch = self.repo.default_branch or "main"
                title = f"✨ Feature: {task_name}"
                body = f"""### ✅ AI Task Completed

    This PR implements the feature: **{task_name}**

    Closes #{issue_number}
    """
                pr = await self.repo.create_pull(title=title, body=body, head=branch_name, base=default_branch)
                logger.info(f"✅ Pull Request Created: {pr.html_url}")
                return pr.number
            except Exception as e:
                logger.error(f"❌ Failed to create pull request: {e}")
                raise

    def auto_merge_pr(self, pr_number: int) -> None:
        try:
            pr = self.repo.pull_request(pr_number)
            if pr.is_mergeable():
                pr.merge(commit_message="✅ Auto-merging AI-generated PR after passing checks.")
                logger.info(f"✅ PR #{pr_number} successfully merged!")
            else:
                logger.warning(f"⚠️ PR #{pr_number} not mergeable. Manual review needed.")
        except Exception as e:
            logger.error(f"❌ Auto-merge failed for PR #{pr_number}: {e}")

    def trigger_ci_cd(self, workflow: str = 'depoly') -> None:
        url = f"https://api.github.com/repos/{Settings.GITHUB_REPO}/actions/workflows/{workflow}.yml/dispatches"
        headers = {
            "Authorization": f"token {Settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {"ref": "main"}
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 204:
            print("✅ CI/CD Pipeline Triggered Successfully!")
        else:
            print(f"❌ Failed to trigger CI/CD: {response.text}")

    def to_bytes_if_needed(self, content):
        return content if isinstance(content, bytes) else content.encode("utf-8")
