class File:
    def __init__(self, file_path: str, exists: bool = False):
        self.file_path = file_path
        self.exists = exists

class Image(File):
    def __init__(self, file_path: str, exists: bool = False):
        super().__init__(file_path, exists)
        self.shape = None

class ClassImage(Image):
    def __init__(self, file_path: str, exists: bool = False):
        super().__init__(file_path, exists)
        self.class_id = None
        self.class_label = None

class ImageGroup:
    def __init__(self, images: list):
        self.balance_ratio: list = []
        self.data = images
        self.group_name = None

class Dataset:
    def __init__(self, images: list):
        self.grouped = False
        self.images = images
        if len(images) > 0 and isinstance(images[0], ImageGroup):
            self.grouped = True
        self.dataset_name = None
        self.dataset_task = None
        self.balance_ratio: list = []
        self.split_ratio: list = []
        
        if self.grouped is True:
            self.num_images = sum(len(group.data) for group in images)
        else:
            self.num_images = len(images)