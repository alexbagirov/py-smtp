from argparser import Parser
from simple import run
from batch import BatchSender


def main() -> None:
    parser = Parser()
    args = parser.parse()
    if args.batch:
        sender = BatchSender(args.batch, args)
        sender.broadcast()
    else:
        run(args)


if __name__ == '__main__':
    main()
