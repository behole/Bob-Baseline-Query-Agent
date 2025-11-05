#!/usr/bin/env python3
"""
GEO Audit Platform CLI - Main entry point
"""

import click
import json
from pathlib import Path

from geo_audit.core.tracker import GEOTracker
from geo_audit.config.settings import Settings, ClientConfig, load_legacy_config
from geo_audit.utils.query_generator import QueryGenerator


@click.group()
@click.version_option(version="2.0.0")
def cli():
    """
    🎯 GEO Audit Platform - Generative Engine Optimization Tracking

    Track brand visibility across AI platforms (Claude, ChatGPT, Google AI, Perplexity)
    and generate comprehensive competitive intelligence reports.
    """
    pass


@cli.command()
@click.option('--client', '-c', required=True, help='Client name (e.g., "brush_on_block")')
@click.option('--queries', '-q', required=True, type=click.Path(exists=True), help='Path to queries JSON file')
@click.option('--worksheet', '-w', required=True, help='Worksheet name for results')
@click.option('--config', default='config/platforms.yaml', help='Platform config file')
@click.option('--legacy-config', default='config.json', help='Legacy config.json (fallback)')
def track(client, queries, worksheet, config, legacy_config):
    """
    🚀 Run tracking queries across AI platforms

    Example:
        geo-audit track --client restoration_hardware --queries rh_queries.json --worksheet "RH_Audit_2025"
    """
    click.echo("🎯 GEO Audit Platform - Tracking Mode\n")

    # Load configurations
    try:
        # Try new config format first
        if Path(config).exists():
            settings = Settings(config)
            platforms_config = settings.get_platforms_config()
            storage_config = settings.get_storage_config()
        else:
            # Fall back to legacy config
            click.echo(f"⚠️ Using legacy config format: {legacy_config}")
            config_data = load_legacy_config(legacy_config)
            platforms_config = config_data['platforms']
            storage_config = config_data['storage']
    except Exception as e:
        click.echo(f"❌ Error loading platform config: {e}", err=True)
        return

    # Load client configuration
    try:
        client_config = ClientConfig(client)
        brand_name = client_config.get_brand_name()
        industry = client_config.get_industry()
    except Exception as e:
        click.echo(f"⚠️ Could not load client config: {e}")
        brand_name = client.replace('_', ' ').title()
        industry = None

    # Load queries
    try:
        with open(queries, 'r') as f:
            queries_data = json.load(f)
    except Exception as e:
        click.echo(f"❌ Error loading queries: {e}", err=True)
        return

    # Initialize tracker
    try:
        tracker = GEOTracker(
            brand_name=brand_name,
            platforms_config=platforms_config,
            storage_config=storage_config,
            industry=industry
        )
    except Exception as e:
        click.echo(f"❌ Error initializing tracker: {e}", err=True)
        return

    # Run batch
    try:
        summary = tracker.run_query_batch(
            queries=queries_data,
            worksheet_name=worksheet,
            create_worksheet=True
        )

        click.echo("\n✅ Tracking complete!")
        click.echo(f"📊 Results saved to worksheet: {worksheet}")

    except Exception as e:
        click.echo(f"❌ Error during tracking: {e}", err=True)
        return


@cli.command()
@click.option('--config', default='config/platforms.yaml', help='Platform config file')
@click.option('--legacy-config', default='config.json', help='Legacy config.json (fallback)')
def test(config, legacy_config):
    """
    🔍 Test connections to all platforms and storage

    Example:
        geo-audit test
    """
    click.echo("🔍 Testing GEO Audit Platform Connections\n")

    # Load configurations
    try:
        if Path(config).exists():
            settings = Settings(config)
            platforms_config = settings.get_platforms_config()
            storage_config = settings.get_storage_config()
        else:
            click.echo(f"⚠️ Using legacy config format: {legacy_config}")
            config_data = load_legacy_config(legacy_config)
            platforms_config = config_data['platforms']
            storage_config = config_data['storage']
    except Exception as e:
        click.echo(f"❌ Error loading config: {e}", err=True)
        return

    # Initialize tracker (dummy brand for testing)
    try:
        tracker = GEOTracker(
            brand_name="Test Brand",
            platforms_config=platforms_config,
            storage_config=storage_config
        )

        # Run tests
        results = tracker.test_connections()

        # Summary
        click.echo("\n" + "="*50)
        all_pass = all(results.values())
        if all_pass:
            click.echo("✅ All connections successful!")
        else:
            failed = [k for k, v in results.items() if not v]
            click.echo(f"❌ Failed connections: {', '.join(failed)}")
        click.echo("="*50)

    except Exception as e:
        click.echo(f"❌ Error during testing: {e}", err=True)


@cli.command()
@click.argument('client_name')
@click.option('--industry', help='Industry (sunscreen, furniture, skincare, etc.)')
@click.option('--brand', help='Full brand name')
def init(client_name, industry, brand):
    """
    🏗️ Initialize a new client configuration

    Example:
        geo-audit init pottery_barn --industry furniture --brand "Pottery Barn"
    """
    click.echo(f"🏗️ Initializing client: {client_name}\n")

    # Interactive prompts if not provided
    if not brand:
        brand = click.prompt("Brand name", default=client_name.replace('_', ' ').title())

    if not industry:
        industry = click.prompt(
            "Industry",
            type=click.Choice(['sunscreen', 'furniture', 'skincare', 'general']),
            default='general'
        )

    # Create client config
    config_path = Path(f"config/clients/{client_name}.yaml")
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config_content = f"""# Client Configuration: {brand}
brand_name: "{brand}"
industry: "{industry}"

# Custom keywords (optional - auto-generated if not provided)
keywords:
  - "{brand.lower()}"

# Custom competitors (optional - uses industry default if not provided)
competitors: []

# Client-specific settings
settings:
  screenshot_dir: "screenshots/{client_name}"
  report_branding:
    primary_color: "#000000"
    logo_url: ""
"""

    with open(config_path, 'w') as f:
        f.write(config_content)

    click.echo(f"✅ Client config created: {config_path}")
    click.echo(f"📝 Edit the file to customize keywords and competitors")


@cli.command()
@click.option('--client', '-c', required=True, help='Client name')
@click.option('--output', '-o', required=True, help='Output JSON file path')
@click.option('--count', '-n', default=50, help='Total number of queries to generate (default: 50)')
@click.option('--products', '-p', multiple=True, help='Product categories (can specify multiple)')
@click.option('--config', default='config.json', help='Config file for API keys')
def generate(client, output, count, products, config):
    """
    🤖 Generate queries using AI for a client

    Example:
        geo-audit generate --client restoration_hardware --output rh_queries.json --count 60 \\
          --products "outdoor furniture" --products "dining tables" --products "sofas"
    """
    click.echo("🤖 AI-Powered Query Generator\n")

    # Load client configuration
    try:
        client_config = ClientConfig(client)
        brand_name = client_config.get_brand_name()
        industry = client_config.get_industry() or 'general'
        competitors = client_config.get_competitors()
    except Exception as e:
        click.echo(f"❌ Could not load client config: {e}", err=True)
        click.echo("💡 Run: ./geo-audit init <client> first")
        return

    # Get product categories
    if not products:
        products = click.prompt(
            "Product categories (comma-separated)",
            default="products, services"
        ).split(',')
        products = [p.strip() for p in products]

    # Load API key
    try:
        with open(config, 'r') as f:
            config_data = json.load(f)
            api_key = config_data.get('anthropic_api_key')
            if not api_key:
                click.echo("❌ Anthropic API key not found in config", err=True)
                return
    except Exception as e:
        click.echo(f"❌ Error loading config: {e}", err=True)
        return

    click.echo(f"📋 Brand: {brand_name}")
    click.echo(f"🏭 Industry: {industry}")
    click.echo(f"📦 Products: {', '.join(products)}")
    click.echo(f"🎯 Target: {count} queries")
    click.echo(f"⚔️  Competitors: {len(competitors)} loaded\n")

    # Generate queries
    try:
        generator = QueryGenerator(api_key)
        queries = generator.generate_queries(
            brand_name=brand_name,
            industry=industry,
            product_categories=list(products),
            competitors=competitors,
            total_queries=count
        )

        # Save to file
        generator.save_to_file(queries, output)

        click.echo(f"\n✅ Success! Generated {len(queries)} queries")
        click.echo(f"📄 Saved to: {output}")
        click.echo(f"\n💡 Next step: ./geo-audit track --client {client} --queries {output} --worksheet \"Audit_Name\"")

    except Exception as e:
        click.echo(f"❌ Error generating queries: {e}", err=True)
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--worksheet', '-w', required=True, help='Worksheet name to generate report from')
@click.option('--client', '-c', required=True, help='Client name')
@click.option('--output', '-o', required=True, help='Output HTML file path')
@click.option('--type', '-t', default='advanced', type=click.Choice(['standard', 'advanced']), help='Report type')
def report(worksheet, client, output, type):
    """
    📊 Generate a report from tracking data

    Example:
        geo-audit report --worksheet "RH_Audit_2025" --client restoration_hardware --output rh_report.html
    """
    click.echo(f"📊 Generating {type} report...\n")
    click.echo("⚠️ Report generation not yet implemented in new CLI")
    click.echo("💡 Use legacy generate_advanced_report.py for now")


if __name__ == '__main__':
    cli()
