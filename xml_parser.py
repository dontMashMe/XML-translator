import xml.etree.ElementTree as ET
import api_request as API
import re


class XMLParser:
    def __init__(self, file, dest_lang_lid: str):
        self.file = file
        self.tree = ET.parse(self.file)
        self.root = self.tree.getroot()
        self.dest_lang_lid = dest_lang_lid

    # creates and returns new element, while appending it to the tree
    def sub_element_with_text(self, parent, tag, attrib: dict, text: str):
        element = parent.makeelement(tag, attrib)
        parent.append(element)
        element.text = text
        return element

    def insert_new_supported_lang(self, lang: str):
        # first insert the tag in <languages>
        languages = self.root.find('header/languages')
        attributes = {"locked": "false", "lid": self.dest_lang_lid}
        lang = self.sub_element_with_text(parent=languages, tag="lang", text=lang, attrib=attributes)
        print("Inserting new language: {}".format(lang.text))
        self.write_changes()
        # print(ET.tostring(languages))

    def reiterate_untranslated_vals(self):
        literals = self.root.findall('content/literal')
        api_interface = API.APIInterface("EN", self.dest_lang_lid)
        counter = 0
        for literal in literals:
            vals = literal.findall('value')
            for value in vals:
                flag = True
                if value.attrib.get('lid') == self.dest_lang_lid:
                    if value.text is not None:
                        for x in value.text:
                            if re.search(u'[\u4e00-\u9fff]', x):
                                flag = False
                        if flag:
                            counter += 1
                            old_val = value.text
                            value.text = api_interface.translate(value.text)
                            print("Untranslated value: {} at literal: {}\nTranslated to: {}"
                                  .format(old_val, literal.attrib.get('id'), value.text))
                            self.write_changes()
        print("Found {} untranslated values\n".format(counter))

    def insert_new_literal_tags(self):
        literals = self.root.findall('content/literal')
        api_interface = API.APIInterface("EN", self.dest_lang_lid)
        counter = 0
        val_list = []
        skipped_literals = []
        for literal in literals:
            vals = literal.findall('value')
            if self.calc_length_of_values(val_list) + counter < 5000:
                val_list.append(vals)
                skipped_literals.append(literal)
                counter += self.calc_length_of_values(val_list)
            else:
                val_dict = self.translate_vals(val_list, api_interface)
                print(val_dict)

                # remove non eng
                for value_group in val_list:
                    for value in value_group:
                        if value.attrib.get('lid') != "en":
                            value_group.remove(value)
                flat_list = [val for val_group in val_list for val in val_group]
                for idx, val in enumerate(flat_list):
                    if val.text is not None:
                        translation = val_dict[val.text]
                        attrib = {"lid": self.dest_lang_lid}
                        if translation is not None and 'MYMEMORY WARNING' not in translation:
                            value = self.sub_element_with_text(parent=skipped_literals[idx],
                                                               tag="value", text=translation,
                                                               attrib=attrib)
                            print(
                                "Inserting new value: '{}' at literal: {}"
                                    .format(value.text, skipped_literals[idx].attrib.get('id')))
                        else:
                            counter += 1
                            print("Skipping due to either translation not available or MYMEMORY warning.")
                self.write_changes()
                counter = 0
                val_list.clear()
                skipped_literals.clear()
                # append the skipped literal
                skipped_literals.append(literal)
                # append the skipped vals
                val_list.append(vals)

        self.write_changes()

    def calc_length_of_values(self, val_list: list) -> int:
        sum_length = 0
        for val_group in val_list:
            for val in val_group:
                if val.text is not None:
                    sum_length += len(val.text)
        return sum_length

    def translate_vals(self, values, api_interface) -> dict:
        for value_group in values:
            for value in value_group:
                if self.dest_lang_lid in value.get('lid'):
                    value_group.remove(value)
                    print("Skipping translation of: '{}' because it already exists.".format(value.text))
                if value.attrib.get('lid') != 'en' or value.text is None:
                    value_group.remove(value)

        return api_interface.translate_list(values)

    # xmlns attribute tag in root messes with the module in a way that it can't reliable fetch tags by name
    # removing it and adding after job is done is the easiest way of dealing with the problem
    def remove_xmlns_attr(self):
        # del self.root.tag['xmls']
        print(self.root.attrib)

    # writes changes to output file
    def write_changes(self):
        print("SAVING CHANGES.")
        self.tree.write('output1.xml', encoding='utf-16')
