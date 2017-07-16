import errno
import os

from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


class Omniglot(Dataset):
    URLS = [
        'https://github.com/brendenlake/omniglot/raw/master/python/images_background.zip',
        'https://github.com/brendenlake/omniglot/raw/master/python/images_evaluation.zip'
    ]
    raw_folder = 'raw'
    processed_folder = 'processed'

    def __init__(self, root='data/omniglot', transform=None, target_transform=None, download=True):
        self.root = root
        self.transform = transform
        self.target_transform = target_transform
        if download: self.download()

        assert self._check_exists(), 'Dataset not found. You can use download=True to download it'

        self.all_items = find_classes(os.path.join(self.root, self.processed_folder))
        self.classes = index_classes(self.all_items)

    def __getitem__(self, index):
        filename = self.all_items[index][0]
        path = self.all_items[index][2] + "/" + filename
        img = Image.open(path).convert('RGB')
        target = self.classes[self.all_items[index][1]]
        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self):
        return len(self.all_items)

    def _check_exists(self):
        return os.path.exists(os.path.join(self.root, self.processed_folder, "images_evaluation")) and \
               os.path.exists(os.path.join(self.root, self.processed_folder, "images_background"))

    def download(self):
        from six.moves import urllib
        import zipfile

        if self._check_exists():
            return

        try:
            os.makedirs(os.path.join(self.root, self.raw_folder))
            os.makedirs(os.path.join(self.root, self.processed_folder))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        for url in self.URLS:
            print('Downloading %s.' % url)
            data = urllib.request.urlopen(url)
            filename = url.rpartition('/')[2]
            file_path = os.path.join(self.root, self.raw_folder, filename)
            with open(file_path, 'wb') as f:
                f.write(data.read())
            file_processed = os.path.join(self.root, self.processed_folder)

            zip_ref = zipfile.ZipFile(file_path, 'r')
            zip_ref.extractall(file_processed)
            zip_ref.close()
        print("Download finished.")


def find_classes(root_dir):
    classes = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith("png"):
                path = root.split('/')
                classes.append((file, path[len(path) - 2] + "/" + path[len(path) - 1], root))
    return classes


def index_classes(items):
    indices = {}
    for item in items:
        if not item[1] in indices:
            indices[item[1]] = len(indices)
    return indices


if __name__ == "__main__":
    from torch.utils.data import DataLoader

    image_transforms = transforms.Compose([
        transforms.Scale(28),
        transforms.ToTensor()
    ])
    dataset = Omniglot(transform=image_transforms)

    iterator = DataLoader(dataset, 32, shuffle=True, drop_last=True)

    batch = next(iter(iterator))
    images, labels = batch

    print("A normal batch looks like %s w/ labels as %s. " % (str(images.size()), str(labels.size())))
    print("The dataset contains %d dataset samples and %d classes. " % (len(dataset), len(dataset.classes)))