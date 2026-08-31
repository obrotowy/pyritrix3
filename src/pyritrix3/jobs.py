from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pyritrix import pyritrix


class JobsEndpoint:
    def __init__(self, client: pyritrix):
        self._client = client

    def create(self, createpath: str, profile=None) -> dict:
        """
        Creates a new crawl job from the selected profile. 
        If no profile is supplied, Defaults (XML) is used.
        Built-in profiles include Defaults (XML) and Defaults (Groovy).
        Existing job profiles may also be selected by passing the profile job’s short name.
        Arguments:
            createpath: the name of the new job
            profile: optional profile name. Existing profiles use their job short names.
        """
        data = {
            "action": "create",
            "createpath": createpath,
            "profile": profile  # It's fine, requests will omit this if profile=None
        }
        response = self._client.post("/engine", data=data)
        assert response.status_code == 200
        return response.json()

    def add(self, addpath: str) -> dict:
        """
        Adds a new job directory to the Heritrix configuration.
        The directory must contain a cxml configuration file.
        Arguments:
            action: must be add
            addpath: the job directory to add
        """
        data = {
            "action": "add",
            "addpath": addpath
        }
        response = self._client.post("/engine", data=data)
        return response.json()

    def get(self, jobname: str) -> dict:
        """
        Returns status information and statistics about the chosen job.
        """
        return self._client.get(f"/engine/job/{jobname}").json()

    def build(self, jobname: str) -> dict:
        """
        Builds the job configuration for the chosen job. It reads an XML descriptor file and uses
        Spring to build the Java objects that are necessary for running the crawl.
        Before a crawl can be run it must be built.
        """
        data = {"action": "build"}
        response = self._client.post(f"/engine/job/{jobname}", data=data)
        return response.json()

    def launch(self, jobname: str, checkpoint: str) -> dict:
        """
        Launches a crawl job. The job can be launched in the “paused” state or the “unpaused” state.
        If launched in the “unpaused” state the job will immediately begin crawling.
        Arguments:
            checkpoint: optional field. If supplied, Heritrix will attempt to launch from a checkpoint.
                        Should be the name of a checkpoint (e.g. cp00001-20180102121229) or (since version 3.3)
                        the special value latest, which will automatically select the most recent checkpoint.
                        If no checkpoint is specified (or if the latest checkpoint is requested and there
                        are no valid checkpoints) a new crawl will be launched.
        """
        data = {
            "action": "launch",
            "checkpoint": checkpoint
        }
        response = self._client.post(f"/engine/job/{jobname}", data=data)
        return response.json()

    def rescan(self) -> dict:
        """
        Rescans the main job directory and returns an HTML page containing all the job names.
        It also returns information about the jobs, such as the location of the job 
        configuration file and the number of job launches.
        """

        return self._client.post("/engine", data={"action": "rescan"}).json()

    def pause(self, jobname: str):
        """
        Pauses an unpaused job. No crawling will occur while a job is paused.
        """
        return self._client.post(f"/engine/job/{jobname}", data={"action": "pause"}).json()

    def unpause(self, jobname: str):
        """
        This API unpauses a paused job. Crawling will resume (or begin, in the case of
        a job launched in the paused state) if possible.
        """
        return self._client.post(f"/engine/job/{jobname}", data={"action": "unpause"}).json()
