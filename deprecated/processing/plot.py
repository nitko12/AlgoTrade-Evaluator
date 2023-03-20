import pandas as pd
import matplotlib.pyplot as plt


def main():
    df = pd.read_parquet('data/rounds/round_3_augmented.parquet')

    all_pairs = set()

    for col in df.columns:
        if col.startswith('close_'):
            all_pairs.add(tuple(col.split('_')[1].split(',')))

    for pair in all_pairs:

        plt.clf()

        df[[f'close_{pair[0]},{pair[1]}',
            f'original_close_{pair[0]},{pair[1]}']].plot()

        # save to file

        plt.savefig(f"data/plots_round3/{pair[0]}_{pair[1]}.png")


if __name__ == '__main__':
    main()
