from abc import ABC, abstractmethod

class BaseOpenProjectClient(ABC):

    @abstractmethod
    def list_projects(self):
        pass

    @abstractmethod
    def get_projects(self, project_id):
        pass
    
    @abstractmethod
    def list_work_packages(self, project_id):
        pass
    
    @abstractmethod
    def get_work_package(self, work_package_id):
        pass

    @abstractmethod
    def create_work_package(self, project_id):
        pass