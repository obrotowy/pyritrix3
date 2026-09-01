from typing import TYPE_CHECKING, IO

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

    def pause(self, jobname: str) -> dict:
        """
        Pauses an unpaused job. No crawling will occur while a job is paused.
        """
        return self._client.post(f"/engine/job/{jobname}", data={"action": "pause"}).json()

    def unpause(self, jobname: str) -> dict:
        """
        This API unpauses a paused job. Crawling will resume (or begin, in the case of
        a job launched in the paused state) if possible.
        """
        return self._client.post(f"/engine/job/{jobname}", data={"action": "unpause"}).json()

    def terminate(self, jobname: str) -> dict:
        """
        Terminates a runnig job.
        """
        return self._client.post(f"/engine/job/{jobname}", data={"action": "terminate"}).json()

    def teardown(self, jobname: str) -> dict:
        """
        Removes the Spring code that is used to run the job. Once a job is torn down it must be rebuilt in order to run.
        """
        return self._client.post(f"/engine/job/{jobname}", data={"action": "teardown"}).json()

    def copy(self, jobname: str, copyTo: str, asProfile: bool) -> dict:
        """
        Copies an existing job configuration to a new job configuration. If the asProfile option is submitted with value on,
        then the copy is a non-runnable profile. Profiles are listed as options when creating new jobs,
        and profiles with built-in names override the built-ins.
        Arguments:
            copyTo: the name of the new job or profile configuration
            asProfile: whether to copy the job as a runnable configuration or as a non-runnable profile.
                       True means the job will be copied as a profile.
        """
        data = {
            "copyTo": copyTo,
        }
        if asProfile:
            data["asProfile"] = "on"
        return self._client.post(f"/engine/job/{jobname}", data=data).json()

    def delete(self, jobname: str) -> dict:
        """
        Deletes an existing job. It will remove everything related to the job (configuration, statistics, logs and results) 
        including the whole job folder. Everything to keep has to be copied outside of the job folder.

        Deleting a job is only possible if no active application context for the job exists which is
        the case for new or unbuilt jobs. If a job has been built, it must first be torn down to allow deletion.
        """
        return self._client.post(f"/engine/job/{jobname}", data={"action": "delete"}).json()

    def checkpoint(self, jobname: str) -> dict:
        """
        This API checkpoints the chosen job. Checkpointing writes the current state of a crawl 
        to the file system so that the crawl can be recovered if it fails.
        """
        return self._client.post(f"/engine/job/{jobname}", data={"action": "checkpoint"}).json()

    def execute_script(self, jobname: str, engine: str, script: str) -> dict:
        """
        Executes a script. The script can be written as Beanshell, ECMAScript, Groovy, or AppleScript.
        Arguments:
            engine: the script engine to use. One of beanshell, js, groovy or AppleScriptEngine.
            script: the script code to execute
        """
        assert script in ["beanshell", "js", "groovy", "AppleScriptEngine"]
        data = {
            "engine": engine,
            "script": script
        }
        return self._client.post(f"/engine/job/{jobname}/script", data=data).json()

    def submit_config_file(self, jobname: str, file: IO):
        response = self._client.put(f"/engine/job/{jobname}/crawler-beans.cxml", data=file)
        assert response.status_code == 200
