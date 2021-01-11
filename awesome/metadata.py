import assets

if __name__ == '__main__':
    sites, families, pairs, sensors = assets.get_metadata()

    for fam in families:
        print(fam.keys())
        print()
