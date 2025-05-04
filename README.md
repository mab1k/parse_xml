# XML Processor Documentation

## Основные компоненты

### 1. ConfigLoader
**Назначение**: Загрузка параметров из конфигурационного файла

```python
class ConfigLoader:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
    
    def load_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
```

### 2. XMLProcessor
**Назначение**: Основная логика обработки данных

```python
class XMLProcessor:
    def __init__(self, xml_file, config):
        self.xml_file = xml_file
        self.config = config
        self.classes = {}
        self.contained_classes = defaultdict(list)
        self.containment_info = defaultdict(list)
```
## Конфигурация
```json
{
    "xml_tags": {
        "class": "Class",
        "attribute": "Attribute",
        "aggregation": "Aggregation"
    },
    "class_attributes": {
        "name": "name",
        "is_root": "isRoot",
        "documentation": "documentation"
    },
    "attribute_attributes": {
        "name": "name",
        "type": "type"
    },
    "aggregation_attributes": {
        "source": "source",
        "target": "target",
        "multiplicity": "sourceMultiplicity",
        "separator": ".."
    },
    "paths_file_save": {
        "xml_path": "out/config.xml",
        "json_path": "out/meta.json"
    },
    "path_file_input": "test_input.xml"
}
