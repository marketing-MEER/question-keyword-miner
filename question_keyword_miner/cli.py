"""Command line entry point: `question-keyword-miner [--gsc GSC.csv] [--seed TERM --autocomplete]`."""
from pathlib import Path

import click

from . import __version__, core
from .benchmark import STATS
from .report import Report, write_excel


def _split(values):
    return [t.strip() for v in values for t in v.split(",") if t.strip()]


@click.command()
@click.option("--gsc", "gsc_file", type=click.Path(exists=True), default=None,
              help="Search Console queries export (or any keyword CSV).")
@click.option("--seed", "seeds", multiple=True, help="Seed topics, comma separated (repeatable).")
@click.option("--autocomplete/--no-autocomplete", default=False, show_default=True,
              help="Ask Google autocomplete for questions about each seed (network; about 10 requests per seed).")
@click.option("--lang", default="en", show_default=True, help="Autocomplete language.")
@click.option("--country", default="us", show_default=True, help="Autocomplete country.")
@click.option("--delay", default=1.0, show_default=True, help="Seconds between autocomplete requests (min 0.5).")
@click.option("-o", "--output", default="question_keywords", show_default=True,
              help="Report name; writes <name>.html and <name>.xlsx")
@click.version_option(__version__)
def main(gsc_file, seeds, autocomplete, lang, country, delay, output):
    """Collect question keywords from a GSC export and/or Google autocomplete, with the answer format for each.

    Built by Meer Hamza - linkedin.com/in/meerhamza-seo
    """
    seeds = _split(seeds)
    if not gsc_file and not (autocomplete and seeds):
        raise click.UsageError("Give --gsc FILE, or --seed TERM with --autocomplete (or both).")
    gsc = core.load_gsc(gsc_file) if gsc_file else None
    sugg = None
    if autocomplete and seeds:
        click.echo(f"Asking autocomplete for {len(seeds)} seed(s)...")
        sugg = core.autocomplete(seeds, delay=max(delay, 0.5), lang=lang, country=country)
    questions = core.mine(gsc, sugg, seeds)
    types = core.type_summary(questions)
    ov = core.overview(gsc, questions)

    sources = ([Path(gsc_file).name] if gsc_file else []) + ([f"autocomplete: {', '.join(seeds)}"] if sugg is not None else [])
    report = Report(title="Question keyword report", subtitle=" · ".join(sources) + f" · {len(questions):,} questions",
                    tool="question-keyword-miner")
    cards = [("Questions", len(questions), "good"), ("Average words", ov["avg_words"])]
    if ov["question_share_pct"] is not None:
        cards += [("GSC queries", ov["gsc_queries"]), ("Share that are questions", f"{ov['question_share_pct']}%")]
    if sugg is not None:
        cards.append(("New from autocomplete", ov["autocomplete_only"], "warn"))
    report.add_cards(cards)
    report.add_benchmark(STATS[0], how_used="Your share of question queries is shown next to NP Digital's 17%, and "
                         "every question gets an answer format, following the insight 'format answers for featured "
                         "snippets, especially for how and what terms'.")
    report.add_benchmark(STATS[1], how_used="Question searches are growing, so autocomplete questions you don't rank "
                         "for yet are listed as new content to write.")
    report.add_table("Question types", types, sheet="Types",
                     note="Answer formats are general featured-snippet practice.")
    for t in types["type"]:
        g = questions[questions["type"] == t].drop(columns=["type", "answer_format"])
        report.add_table(f"{t} questions", g, sheet=f"{t.replace('/', '-')}")
    report.add_table("All questions", questions, sheet="All questions")

    html_path = report.save_html(Path(output).with_suffix(".html"))
    xlsx_path = write_excel(report.sheets, Path(output).with_suffix(".xlsx"))
    click.secho(f"Report: {html_path}\nData:   {xlsx_path}", fg="green", bold=True)
    click.echo(types[["type", "questions", "impressions"]].to_string(index=False))


if __name__ == "__main__":
    main()
