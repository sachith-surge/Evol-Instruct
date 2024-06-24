import os
import json
from pyprojroot import here
from dataclasses import dataclass
from time import time

from evol_instruct.init.logger import logger


@dataclass
class DataInstance:
    instruction: str
    response: str
    category: str
    evolution_strategy: str
    in_depth_evolving_operation: str
    epoch: int

    def __repr__(self) -> str:
        return f"""DatasetInstance(instruction={self.instruction}, response={self.response}, category={self.category}, evolution_strategy={self.evolution_strategy}, in_depth_evolving_operation={self.in_depth_evolving_operation}, epoch={self.epoch})"""

    def __str__(self) -> str:
        return f"""Dataset Instance
Instruction: {self.instruction}
Response: {self.response}
Category: {self.category}
Evolution Strategy: {self.evolution_strategy}
In-depth Evolving Operation: {self.in_depth_evolving_operation}
Epoch: {self.epoch}"""

class Dataset:
    
    def __init__(
            self, 
            filename_in_disk: str, 
            data: list[DataInstance] = [], 
            save_time_interval: int = 300, 
            save_count_interval: int = 5
    ):
        self.data = data
        self.filename = filename_in_disk
        self.save_time_interval = save_time_interval
        self.save_count_interval = save_count_interval

        self.last_save_time = time()

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        return self.data[index]
    
    def __repr__(self) -> str:
        return f"""Dataset({len(self.data)})"""
    
    def __str__(self) -> str:
        return repr(self)
    
    def add_data(self, instruction: str, response: str, category: str, evolution_strategy: str, in_depth_evolving_operation: str, epoch: int):
        data_instance = DataInstance(
            instruction=instruction,
            response=response,
            category=category,
            evolution_strategy=evolution_strategy,
            in_depth_evolving_operation=in_depth_evolving_operation,
            epoch=epoch
        )
        self.data.append(data_instance)

        self.check_and_save()
    
    def join_data(self, data_instances: list[DataInstance]):
        self.data.extend(data_instances)

    def _to_json(self):
        keys = ("instruction", "response", "category", "evolution_strategy", "in_depth_evolving_operation", "epoch")
        return {key: [getattr(data_instance, key) for data_instance in self] for key in keys}
    
    def check_and_save(self):
        if len(self.data) % self.save_count_interval >= 0 or time() - self.last_save_time >= self.save_time_interval:
            self.save(self.filename)
            self.last_save_time = time()

    def save(self, filename):
        logger.info("Saving dataset")

        if not os.path.exists(os.path.dirname(os.path.join(os.getcwd(), filename))):
            os.makedirs(os.path.dirname(filename))

        with open(here(filename), "w") as f:
            json.dump(self._to_json(), f)

# Testing
dataset = Dataset(filename_in_disk="test.json")

dataset.add_data(
    instruction="hello",
    response="hi0",
    category="test0",
    evolution_strategy="test0",
    in_depth_evolving_operation="test0",
    epoch=0
)
dataset.add_data(
    instruction="hello",
    response="hi1",
    category="test1",
    evolution_strategy="test1",
    in_depth_evolving_operation="test1",
    epoch=1
)
dataset.add_data(
    instruction="hello",
    response="hi2",
    category="test2",
    evolution_strategy="test2",
    in_depth_evolving_operation="test2",
    epoch=2
)

dataset.add_data(
    instruction="hello",
    response="hi3",
    category="test3",
    evolution_strategy="test3",
    in_depth_evolving_operation="test3",
    epoch=3
)

dataset.add_data(
    instruction="hello",
    response="hi4",
    category="test4",
    evolution_strategy="test4",
    in_depth_evolving_operation="test4",
    epoch=4
)

dataset.add_data(
    instruction="hello",
    response="hi5",
    category="test5",
    evolution_strategy="test5",
    in_depth_evolving_operation="test5",
    epoch=5
)

dataset.add_data(
    instruction="hello",
    response="hi6",
    category="test6",
    evolution_strategy="test6",
    in_depth_evolving_operation="test6",
    epoch=6
)