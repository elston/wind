from esios_test import load_esios_data


def main():
    data = load_esios_data()
    data.data.to_csv('../data/esios/esios.csv')


if __name__ == '__main__':
    main()
