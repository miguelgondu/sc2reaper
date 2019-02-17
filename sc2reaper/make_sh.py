from glob import glob

def main():
    files = glob("/home/mgd/StarCraftII/Replays/*.SC2Replay")
    script = "replay_parser.py"
    print(f"files: {files}")

    with open("to_run.sh", mode="w") as to_run:
        for f in files[:10]:
            to_run.write(f"sc2reaper ingest {f}\n")

if __name__ == '__main__':
    main()
