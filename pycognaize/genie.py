import time
from typing import Optional

import requests
from pycognaize import Model

try:
    # noinspection PyPackageRequirements
    from loguru import logger
except ImportError:
    from logging import getLogger
    logger = getLogger(__name__)


class Genie:
    CREATE_TASK_ENDPOINT = "document/modelinput"
    RUN_MODEL_ENDPOINT = "data"
    DIGEST_ENDPOINT = "document/digest"

    def __init__(self, model, x_auth, base_url):

        self.model = model
        self.x_auth = x_auth
        self.base_url = base_url.strip('/') + '/'

    def execute(self, document_id: str, recipe_id: str,
                digest: Optional[bool] = False):
        task_id_response = self.create_and_get_task_id(document_id=document_id,
                                                       recipe_id=recipe_id)
        task_id_response.raise_for_status()
        task_id = task_id_response.json()['taskId']
        logger.info(f"Running the model on task {task_id}")
        start = time.time()
        self.run_model(model=self.model, task_id=task_id)
        duration = time.time() - start
        logger.info(f"Model finished in {duration}")
        if digest:
            logger.info("Digesting model results")
            self.digest_results(task_id=task_id)

    def create_and_get_task_id(self, document_id: str,
                               recipe_id: str) -> requests.Response:
        url = self.base_url + self.CREATE_TASK_ENDPOINT
        payload = {'documentId': document_id, 'recipeId': recipe_id}
        headers = {'x-auth': self.x_auth, 'content-type': "application/json"}
        response = requests.request("POST", url, json=payload,
                                    headers=headers)
        response.raise_for_status()
        return response

    def run_model(self, model: Model, task_id: str) -> requests.Response:
        url = self.base_url + self.RUN_MODEL_ENDPOINT
        response = model.execute_genie_v2(task_id=task_id,
                                          token=self.x_auth,
                                          url=url)
        response.raise_for_status()
        return response

    def digest_results(self, task_id: str) -> requests.Response:
        url = self.base_url + self.DIGEST_ENDPOINT
        payload = {'taskId': task_id}
        headers = {'x-auth': self.x_auth, 'content-type': "application/json"}
        response = requests.request("POST", url, data=payload,
                                    headers=headers)
        response.raise_for_status()
        logger.info(response.text)
        return response
