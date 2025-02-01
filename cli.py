import click
import toml
import json
import script

@click.command()
@click.option("--input_folder", "-i")
@click.option("--input_name_start", "-ns", default="")
@click.option("--animation_name", "-n")
@click.option("--output_path")
@click.option("--frame_rate", "-f", type=int)
@click.option("--resource_pack_path")
@click.option("--provider_path")
@click.option("--characters", "-c")
@click.option("--identifier_color", type=int)
@click.option("--options_file", default="script_options.toml")
def main(
    options_file,
    **names
    ):
    data = toml.load(options_file)
    
    missing = False
    for key, val in names.items():
        if val is not None:
            data[key] = val
        if val is None and data.get(key) is None:
            click.echo(f"missing parameter: {key}", err=True)
            missing = True

    if type(data["characters"]) != list:
        print(data["characters"])
        data["characters"] = json.loads(data["characters"])

    if not missing:
        script.run_script(**data)

if __name__ == "__main__":
    main()