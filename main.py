import xml.etree.ElementTree as ET
import json
from collections import defaultdict
from xml.dom import minidom


class ConfigLoader:
    """Класс для загрузки конфигурационного файла"""
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)

    def load_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)


class XMLProcessor:
    """Основной класс для обработки XML данных"""
    def __init__(self, xml_file, config):
        self.xml_file = xml_file
        self.config = config
        self.classes = {}
        self.contained_classes = defaultdict(list)
        self.containment_info = defaultdict(list)

    def parse_xml(self):
        """Парсинг XML-файла"""
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        tags = self.config['xml_tags']
        class_attrs = self.config['class_attributes']
        attr_attrs = self.config['attribute_attributes']
        agg_attrs = self.config['aggregation_attributes']

        for elem in root:
            if tags['class'] in elem.tag:
                class_name = elem.attrib[class_attrs['name']]
                attributes = [{"name": attr.attrib[attr_attrs['name']],
                               "type": attr.attrib[attr_attrs['type']]}
                              for attr in elem.findall(tags['attribute'])]
                self.classes[class_name] = {
                    'is_root': elem.attrib.get(class_attrs['is_root'], 'false') == 'true',
                    'documentation': elem.attrib.get(class_attrs['documentation'], ''),
                    'attributes': attributes
                }

            if tags['aggregation'] in elem.tag:
                source = elem.attrib[agg_attrs['source']]
                target = elem.attrib[agg_attrs['target']]
                multiplicity = elem.attrib.get(agg_attrs['multiplicity'])
                if agg_attrs["separator"] in multiplicity:
                    min_val, max_val = multiplicity.split(agg_attrs["separator"])
                else:
                    min_val = max_val = multiplicity

                self.contained_classes[target].append(source)
                self.containment_info[source].append({
                    'class': source,
                    'min': min_val,
                    'max': max_val
                })

    def generate_json(self):
        """Генерация JSON"""
        json_result = []
        for class_name, class_data in self.classes.items():
            parameters = class_data['attributes'] + [{"name": contained, "type": "class"}
                                                     for contained in self.contained_classes.get(class_name, [])]

            containment = self.containment_info.get(class_name)
            if containment:
                agg_info = containment[0]
                json_result.append({
                    "class": class_name,
                    "documentation": class_data['documentation'],
                    "isRoot": class_data['is_root'],
                    "min": agg_info["min"],
                    "max": agg_info["max"],
                    "parameters": parameters
                })
            else:
                json_result.append({
                    "class": class_name,
                    "documentation": class_data['documentation'],
                    "isRoot": class_data['is_root'],
                    "parameters": parameters
                })

        return json_result

    def generate_xml(self):
        """Генерация XML"""
        def build_xml(class_name, parent=None):
            if parent is None:
                parent = ET.Element(class_name)
            else:
                parent = ET.SubElement(parent, class_name)

            for attr in self.classes.get(class_name, {}).get('attributes', []):
                attr_elem = ET.SubElement(parent, attr['name'])
                attr_elem.text = attr['type']

            for nested_class in self.contained_classes.get(class_name, []):
                build_xml(nested_class, parent)

            return parent

        root_class = next((name for name, data in self.classes.items() if data['is_root']), None)
        if not root_class:
            raise ValueError("Не найден корень в XML")

        xml_tree = build_xml(root_class)

        def indent(elem, level=0):
            i = "\n" + level * "    "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "    "
                for child in elem:
                    indent(child, level + 1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i

        indent(xml_tree)
        xml_str = ET.tostring(xml_tree, encoding='unicode')
        xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ")
        xml_str = '\n'.join(line for line in xml_str.split('\n') if line.strip())

        return xml_str


if __name__ == "__main__":
    config_loader = ConfigLoader()
    processor = XMLProcessor(config_loader.config["path_file_input"], config_loader.config)

    try:
        processor.parse_xml()
        json_output = processor.generate_json()
        xml_output = processor.generate_xml()

        with open(config_loader.config["paths_file_save"]["json_path"], 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=4, ensure_ascii=False)
        print("JSON файл успешно создан: output.json")

        with open(config_loader.config["paths_file_save"]["xml_path"], 'w', encoding='utf-8') as f:
            f.write(xml_output)
        print("XML файл успешно создан: output.xml")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
