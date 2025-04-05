from pathlib import Path

import yaml
from cooklang import parse

CANONICAL_TESTS_FILE = Path(__file__).parent.parent / 'tests' / "canonical.yaml"

canonicals = yaml.safe_load(CANONICAL_TESTS_FILE.read_text(encoding="utf-8"))

tests = canonicals['tests']
test_names = tests.keys()


class Parser():
    def __init__(self):
        from pathlib import Path
        from lark import Lark, Token
        

        path_cooklang_grammar = Path(__file__).parent / "cooklang.lark"

        with open(path_cooklang_grammar, 'r', encoding='utf-8') as f:
            cooklang_grammar = f.read()

        self.lexer = Lark(cooklang_grammar, regex=True)

    def tokenize(self, input_text):
        tokens = self.lexer.lex(input_text)

        return tokens
    
    def parse(self, input_text):
        tokens = self.tokenize(input_text)

        steps = [[]]
        metadata = {}

        curr_text = ""

        for token in tokens:

            if token.type == "MULTIPLE_BLANK_LINES":
                if curr_text:
                    steps[-1].append({'type': 'text', 'value': curr_text})
                    curr_text = ""
                steps.append([])
                continue

            elif curr_text and token.type == "BLANK_LINE":
                curr_text += " "
                continue

            if token.type == "TEXT_ITEM":
                curr_text += token.value

            if curr_text and not token.type == "TEXT_ITEM":
                steps[-1].append({'type': 'text', 'value': curr_text})
                curr_text = ""

            if token.type in ["INGREDIENT", "COOKWARE", "TIMER"]:
                steps[-1].append(handle_token(token))

            if token.type == 'YAML_METADATA':
                metadata = handle_metadata(token, metadata)

        if curr_text and curr_text != " ":
            steps[-1].append({'type': 'text', 'value': curr_text[:-1]})

        if not steps[-1]:
            steps = steps[:-1]

        return {'steps': steps, 'metadata': metadata}
    
    def debug_tests(self, tests):
        num_tests = len(tests)
        for ind, test_name in enumerate(tests.keys()):
            # print(ind)
            
            source = tests[test_name]['source']
            # print(list(self.tokenize(source)))
            expected = tests[test_name]['result']
            produced = self.parse(source)

            if expected!=produced:
                print(f"Passed {ind}/{num_tests}")
                print(f"Test name: {test_name}")

                print("source: " + repr(f"{source}"))
                print()

                print(f"expected: {expected}")
                print(f"produced: {produced}")

                tokens = self.tokenize(source)
                print(f"Tokens: {list(tokens)}")
                break



def handle_metadata(token, metadata):
    import yaml

    if token.type == 'YAML_METADATA':
        yaml_metadata = yaml.safe_load_all(token.value)
        yaml_metadata = list(yaml_metadata)

        for yaml_metadata_info in list(yaml_metadata):
            if yaml_metadata_info is None:
                break

            if type(yaml_metadata_info) is dict:
                for key, value in yaml_metadata_info.items():
                    metadata[key] = value

            elif type(yaml_metadata_info) is str:
                key, value = yaml_metadata_info.split(':')
                key, value = key.strip(), value.strip()
                metadata[key] = value

    return metadata

def handle_token(token):
    def parse_amount(amount):
        units = ""
        if "%" not in amount:
            quantity = amount
        else:
            quantity, units = amount.split('%')
            
        return quantity.strip(), units.strip()


    def parse_quantity(quantity):
        if type(quantity) == str and quantity.isdigit():
            quantity = float(quantity)

        elif quantity.count('/')==1:
            num, denum = quantity.split('/')
            num, denum = num.strip(), denum.strip()

            non_zeros = "123456789"
            if num[0] in non_zeros and denum[0] in non_zeros:
                if num.isdigit() and denum.isdigit():
                    quantity = float(num) / float(denum)

        try:
            quantity = float(quantity)
        except ValueError:
            pass

        return quantity

    value = token.value

    units = ""
    quantity = ""

    if '{' in value:
        ind_open_curly = value.index('{')

        name = value[1:ind_open_curly].strip()
        amount = value[ind_open_curly+1:-1]
        quantity, units = parse_amount(amount)

    else:
        name = value[1:]

    quantity = parse_quantity(quantity)

    if not quantity:
        if token.type == "INGREDIENT":
            quantity = "some"

        elif token.type == "COOKWARE":
            quantity = 1

    return {'type': token.type.lower(), 'name': name, 'quantity': quantity, 'units': units}

if __name__ == '__main__':
    ClangParser = Parser()
    test_name = list(test_names)[0]

    source = tests[test_name]['source']
    # tokens = ClangParser.tokenize(source)

    ClangParser.debug_tests(tests)

