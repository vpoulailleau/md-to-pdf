import argparse
import importlib.resources
import pkg_resources
import sys
from pathlib import Path
from typing import Union

import markdown2
import simplelogging
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

log = None


def md_to_pdf(path_to_md: Union[str, Path], author: str, title: str, size: str) -> None:
    path_to_md = Path(str(path_to_md))
    log.info("Converting %s to HTML", str(path_to_md))
    html = markdown2.markdown_path(
        path_to_md,
        extras=[
            "fenced-code-blocks",
            "cuddled-lists",
            "strike",
            "target-blank-links",
            "tables",
            "metadata",  # TODO for headers, footers…
            "header-ids",
        ],
    )

    # TODO write to a temporary file
    html_path = path_to_md.parent / (path_to_md.stem + ".html")
    with open(html_path, "w", encoding="utf-8") as html_file:
        html_file.write(html)

    log.info("Converting %s to PDF", str(path_to_md))
    pdf_path = path_to_md.parent / (path_to_md.stem + ".pdf")
    font_config = FontConfiguration()
    pdf_writer = HTML(string=html)
    css = CSS(
        string=importlib.resources.read_text("md_to_pdf", "main.css"),
        font_config=font_config,
    )
    css_size = CSS(
        string=importlib.resources.read_text("md_to_pdf", f"{size}.css"),
        font_config=font_config,
    )
    css_custom = CSS(
        string=f"""
          @page {{
            @top-left {{
              content: "{title}";
            }}
            @bottom-left {{
              content: "{author}";
            }}
          }}
        """,
        font_config=font_config,
    )
    pdf_writer.write_pdf(
        pdf_path, stylesheets=[css, css_size, css_custom], font_config=font_config
    )


def main():
    """Entry point."""
    global log

    parser = argparse.ArgumentParser(description="Markdown to PDF converter")
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="increase verbosity level"
    )
    parser.add_argument("-t", "--title", help="title of the document", default="")
    parser.add_argument("-a", "--author", help="author of the document", default="")
    parser.add_argument(
        "-s",
        "--size",
        help="size of the document",
        default="A4",
        choices=["A4", "A5"],
    )
    files = parser.add_mutually_exclusive_group(required=True)
    files.add_argument(
        "-i",
        "--input-path",
        metavar="PATH",
        type=str,
        help="path of the markdown files to convert",
        default=[],
        # allow the user to provide no path at all,
        # this helps writing scripts
        nargs="+",
    )
    # TODO file on the web, with requests
    files.add_argument("--version", action="store_true", help="return version")
    args = parser.parse_args()

    if args.version:
        print(pkg_resources.get_distribution("md_to_pdf").version)
        sys.exit(0)

    log = simplelogging.get_logger("__main__")

    if args.verbose < 1:
        log.reduced_logging()
    elif args.verbose < 2:
        log.normal_logging()
    else:
        log.full_logging()

    for md_path in args.input_path:
        md_to_pdf(md_path, author=args.author, title=args.title, size=args.size)


if __name__ == "__main__":
    main()
