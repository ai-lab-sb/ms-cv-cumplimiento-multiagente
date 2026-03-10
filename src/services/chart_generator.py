"""
Genera gráficos financieros como imágenes PNG codificadas en base64,
listas para embeber directamente en el HTML/PDF del SLIP.
Usa matplotlib sin necesidad de un display (backend Agg).
"""
import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


BOLIVAR_GREEN = "#00694e"
BOLIVAR_GOLD = "#f2a900"
GRAY = "#a0aec0"
FONT_FAMILY = "sans-serif"


def _parse_numeric(value) -> float:
    """Convierte un valor a float, limpiando símbolos de moneda y porcentaje."""
    if value is None:
        return 0.0
    s = str(value).replace("$", "").replace("%", "").replace(",", "").replace(".", "").strip()
    if not s or s == "—":
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def generar_grafico_cliente_anual(datos_financieros: dict) -> str | None:
    """
    Gráfico de barras: indicadores del cliente Año Actual vs Año Anterior.
    Retorna imagen PNG en base64 o None si no hay datos.
    """
    ind_cliente = datos_financieros.get("indicadores_cliente")
    if not ind_cliente:
        return None

    labels = ["Razón Corriente", "Nivel\nEndeudamiento (%)", "Margen\nEBITDA (%)"]
    actual = [
        _parse_numeric(ind_cliente.get("razon_corriente", {}).get("actual")),
        _parse_numeric(ind_cliente.get("nivel_endeudamiento", {}).get("actual")),
        _parse_numeric(ind_cliente.get("margen_ebitda", {}).get("actual")),
    ]
    anterior = [
        _parse_numeric(ind_cliente.get("razon_corriente", {}).get("anterior")),
        _parse_numeric(ind_cliente.get("nivel_endeudamiento", {}).get("anterior")),
        _parse_numeric(ind_cliente.get("margen_ebitda", {}).get("anterior")),
    ]

    if all(v == 0 for v in actual + anterior):
        return None

    anio_actual = datos_financieros.get("anio_actual", "Año Actual")
    anio_anterior = datos_financieros.get("anio_anterior", "Año Anterior")

    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(labels))
    width = 0.35

    bars1 = ax.bar([i - width / 2 for i in x], actual, width, label=str(anio_actual), color=BOLIVAR_GREEN)
    bars2 = ax.bar([i + width / 2 for i in x], anterior, width, label=str(anio_anterior), color=GRAY)

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_title("Indicadores Financieros: Año Actual vs Anterior", fontsize=13, fontweight="bold", color=BOLIVAR_GREEN, pad=12)
    ax.legend(fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))

    for bar_group in [bars1, bars2]:
        for bar in bar_group:
            h = bar.get_height()
            if h != 0:
                ax.annotate(f"{h:.1f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, 4), textcoords="offset points",
                            ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    return _fig_to_base64(fig)


def generar_grafico_cliente_vs_sector(datos_financieros: dict) -> str | None:
    """
    Gráfico de barras: indicadores del cliente vs sector.
    Retorna imagen PNG en base64 o None si no hay datos.
    """
    ind_cliente = datos_financieros.get("indicadores_cliente")
    ind_sector = datos_financieros.get("indicadores_sector")
    if not ind_cliente or not ind_sector:
        return None

    labels = ["Razón Corriente", "Nivel\nEndeudamiento (%)", "Margen\nEBITDA (%)"]
    cliente = [
        _parse_numeric(ind_cliente.get("razon_corriente", {}).get("actual")),
        _parse_numeric(ind_cliente.get("nivel_endeudamiento", {}).get("actual")),
        _parse_numeric(ind_cliente.get("margen_ebitda", {}).get("actual")),
    ]
    sector = [
        _parse_numeric(ind_sector.get("razon_corriente")),
        _parse_numeric(ind_sector.get("nivel_endeudamiento")),
        _parse_numeric(ind_sector.get("margen_ebitda")),
    ]

    if all(v == 0 for v in sector):
        return None

    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(labels))
    width = 0.35

    bars1 = ax.bar([i - width / 2 for i in x], cliente, width, label="Cliente", color=BOLIVAR_GREEN)
    bars2 = ax.bar([i + width / 2 for i in x], sector, width, label="Sector", color=BOLIVAR_GOLD)

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_title("Indicadores Financieros: Cliente vs Sector", fontsize=13, fontweight="bold", color=BOLIVAR_GREEN, pad=12)
    ax.legend(fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))

    for bar_group in [bars1, bars2]:
        for bar in bar_group:
            h = bar.get_height()
            if h != 0:
                ax.annotate(f"{h:.1f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, 4), textcoords="offset points",
                            ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    return _fig_to_base64(fig)


def generar_graficos_financieros(datos_financieros: dict) -> dict:
    """
    Genera ambos gráficos financieros.
    Retorna dict con claves 'grafico_anual' y 'grafico_sector',
    cada una con el string base64 de la imagen o None.
    """
    return {
        "grafico_anual": generar_grafico_cliente_anual(datos_financieros),
        "grafico_sector": generar_grafico_cliente_vs_sector(datos_financieros),
    }
