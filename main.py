from xml_parser import XMLParser

# ----- CHANGE THESE ONLY ------
language = "Chinese"
lid = "zh-cn"  # https://www.science.co.il/language/Locale-codes.php
xml_file = 'bskernel.xmls'
# ------------------------------

# step 1 load xml file
xml_parser = XMLParser(xml_file, dest_lang_lid=lid)
# step 2 insert new language
xml_parser.insert_new_supported_lang(lang=language)
# step 3 translate literals and write output file
xml_parser.insert_new_literal_tags()
# step 4 reiterate through xml and translate skipped values
xml_parser.reiterate_untranslated_vals()
