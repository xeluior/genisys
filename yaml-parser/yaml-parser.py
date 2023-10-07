import pathlib
import yaml

yaml = yaml()
path = pathlib.Path('test.yml')


def parseYaml(fileName):
    with open('my_file.yaml') as file:
        l = yaml.load(file)
        print(l)

def main():
    parseYaml('test.yml')

if __name__ == '__main__':
    main()