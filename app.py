from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import datetime
import json

# ── Region lookup ─────────────────────────────────────────────────────────────
COUNTRY_REGIONS = {
    "Algeria":"Africa","Angola":"Africa","Benin":"Africa","Botswana":"Africa","Burkina Faso":"Africa",
    "Burundi":"Africa","Cabo Verde":"Africa","Cameroon":"Africa","Central African Republic":"Africa",
    "Chad":"Africa","Comoros":"Africa","Congo, Dem. Rep.":"Africa","Congo, Rep.":"Africa",
    "Cote d'Ivoire":"Africa","Djibouti":"Africa","Egypt, Arab Rep.":"Africa","Equatorial Guinea":"Africa",
    "Eritrea":"Africa","Eswatini":"Africa","Ethiopia":"Africa","Gabon":"Africa","Gambia, The":"Africa",
    "Ghana":"Africa","Guinea":"Africa","Guinea-Bissau":"Africa","Kenya":"Africa","Lesotho":"Africa",
    "Liberia":"Africa","Libya":"Africa","Madagascar":"Africa","Malawi":"Africa","Mali":"Africa",
    "Mauritania":"Africa","Mauritius":"Africa","Morocco":"Africa","Mozambique":"Africa","Namibia":"Africa",
    "Niger":"Africa","Nigeria":"Africa","Rwanda":"Africa","Sao Tome and Principe":"Africa","Senegal":"Africa",
    "Seychelles":"Africa","Sierra Leone":"Africa","Somalia":"Africa","South Africa":"Africa",
    "South Sudan":"Africa","Sudan":"Africa","Tanzania":"Africa","Togo":"Africa","Tunisia":"Africa",
    "Uganda":"Africa","Zambia":"Africa","Zimbabwe":"Africa",
    "Antigua and Barbuda":"Americas","Argentina":"Americas","Bahamas, The":"Americas","Barbados":"Americas",
    "Belize":"Americas","Bolivia":"Americas","Brazil":"Americas","Canada":"Americas","Chile":"Americas",
    "Colombia":"Americas","Costa Rica":"Americas","Cuba":"Americas","Dominica":"Americas",
    "Dominican Republic":"Americas","Ecuador":"Americas","El Salvador":"Americas","Grenada":"Americas",
    "Guatemala":"Americas","Guyana":"Americas","Haiti":"Americas","Honduras":"Americas","Jamaica":"Americas",
    "Mexico":"Americas","Nicaragua":"Americas","Panama":"Americas","Paraguay":"Americas","Peru":"Americas",
    "St. Kitts and Nevis":"Americas","St. Lucia":"Americas","St. Vincent and the Grenadines":"Americas",
    "Suriname":"Americas","Trinidad and Tobago":"Americas","United States":"Americas","Uruguay":"Americas",
    "Venezuela, RB":"Americas",
    "Afghanistan":"Asia","Armenia":"Asia","Azerbaijan":"Asia","Bahrain":"Asia","Bangladesh":"Asia",
    "Bhutan":"Asia","Brunei Darussalam":"Asia","Cambodia":"Asia","China":"Asia","Georgia":"Asia",
    "India":"Asia","Indonesia":"Asia","Iran, Islamic Rep.":"Asia","Iraq":"Asia","Israel":"Asia",
    "Japan":"Asia","Jordan":"Asia","Kazakhstan":"Asia","Korea, Dem. People's Rep.":"Asia",
    "Korea, Rep.":"Asia","Kuwait":"Asia","Kyrgyz Republic":"Asia","Lao PDR":"Asia","Lebanon":"Asia",
    "Malaysia":"Asia","Maldives":"Asia","Mongolia":"Asia","Myanmar":"Asia","Nepal":"Asia","Oman":"Asia",
    "Pakistan":"Asia","Philippines":"Asia","Qatar":"Asia","Saudi Arabia":"Asia","Singapore":"Asia",
    "Sri Lanka":"Asia","Syrian Arab Republic":"Asia","Tajikistan":"Asia","Thailand":"Asia",
    "Timor-Leste":"Asia","Turkey":"Asia","Turkmenistan":"Asia","United Arab Emirates":"Asia",
    "Uzbekistan":"Asia","Vietnam":"Asia","West Bank and Gaza":"Asia","Yemen, Rep.":"Asia",
    "Albania":"Europe","Andorra":"Europe","Austria":"Europe","Belarus":"Europe","Belgium":"Europe",
    "Bosnia and Herzegovina":"Europe","Bulgaria":"Europe","Croatia":"Europe","Cyprus":"Europe",
    "Czech Republic":"Europe","Denmark":"Europe","Estonia":"Europe","Finland":"Europe","France":"Europe",
    "Germany":"Europe","Greece":"Europe","Hungary":"Europe","Iceland":"Europe","Ireland":"Europe",
    "Italy":"Europe","Kosovo":"Europe","Latvia":"Europe","Liechtenstein":"Europe","Lithuania":"Europe",
    "Luxembourg":"Europe","Malta":"Europe","Moldova":"Europe","Monaco":"Europe","Montenegro":"Europe",
    "Netherlands":"Europe","North Macedonia":"Europe","Norway":"Europe","Poland":"Europe","Portugal":"Europe",
    "Romania":"Europe","Russian Federation":"Europe","San Marino":"Europe","Serbia":"Europe",
    "Slovak Republic":"Europe","Slovenia":"Europe","Spain":"Europe","Sweden":"Europe","Switzerland":"Europe",
    "Ukraine":"Europe","United Kingdom":"Europe",
    "Australia":"Oceania","Fiji":"Oceania","Kiribati":"Oceania","Marshall Islands":"Oceania",
    "Micronesia, Fed. Sts.":"Oceania","Nauru":"Oceania","New Zealand":"Oceania","Palau":"Oceania",
    "Papua New Guinea":"Oceania","Samoa":"Oceania","Solomon Islands":"Oceania","Tonga":"Oceania",
    "Tuvalu":"Oceania","Vanuatu":"Oceania",
}

# ── Per-country net growth (people/sec) from UN birth/death rates ─────────────
COUNTRY_GROWTH = {
    "India":8.5,"China":1.2,"United States":1.5,"Indonesia":2.1,"Pakistan":4.8,
    "Brazil":1.6,"Nigeria":7.8,"Bangladesh":2.4,"Russia":-0.5,"Ethiopia":4.2,
    "Mexico":1.7,"Japan":-0.9,"Philippines":2.8,"Egypt":3.2,"DR Congo":4.9,
    "Vietnam":1.2,"Iran":1.1,"Turkey":1.2,"Germany":0.1,"Thailand":0.2,
    "United Kingdom":0.5,"France":0.4,"Tanzania":3.9,"South Africa":1.0,
    "Myanmar":0.8,"Kenya":2.8,"South Korea":0.0,"Colombia":1.0,"Spain":0.1,
    "Uganda":4.1,"Iraq":3.1,"Algeria":1.9,"Sudan":2.8,"Ukraine":-0.8,
    "Argentina":0.7,"Afghanistan":3.3,"Poland":-0.1,"Canada":1.2,"Morocco":1.1,
    "Saudi Arabia":1.8,"Mozambique":3.2,"Peru":1.0,"Angola":4.1,"Ghana":2.5,
    "Yemen":2.5,"Nepal":1.1,"Uzbekistan":1.8,"Venezuela":0.5,"Madagascar":3.5,
    "Cameroon":3.2,"Niger":5.1,"Mali":4.2,"Burkina Faso":3.4,"Malawi":3.2,
    "Zambia":3.2,"Romania":-0.5,"Syria":0.8,"Chile":0.6,"Ecuador":1.0,
    "Guatemala":2.1,"Netherlands":0.3,"Cambodia":1.1,"Zimbabwe":2.0,"Senegal":3.0,
    "Chad":4.0,"Somalia":3.5,"Guinea":3.5,"Rwanda":2.8,"Bolivia":1.4,
    "Belgium":0.3,"Haiti":1.5,"Tunisia":0.8,"Cuba":-0.1,"Jordan":1.6,
    "Greece":-0.3,"Czech Republic":0.1,"Portugal":-0.2,"Sweden":0.4,
    "Azerbaijan":0.6,"Hungary":-0.3,"Honduras":1.7,"Tajikistan":2.4,
    "Belarus":-0.2,"Papua New Guinea":2.3,"Togo":2.8,"Libya":1.3,"Laos":1.5,
    "Paraguay":1.3,"Sierra Leone":3.2,"El Salvador":0.6,"Israel":1.8,
    "Nicaragua":1.1,"Kyrgyzstan":1.9,"Denmark":0.3,"Finland":0.1,
    "Slovakia":0.0,"Singapore":0.8,"Norway":0.5,"New Zealand":0.7,
    "Australia":1.1,"Kazakhstan":0.9,"Turkmenistan":1.8,"Sri Lanka":0.4,
    "United Arab Emirates":2.0,"Qatar":1.5,"Kuwait":1.5,"Liberia":3.2,
    "Eritrea":2.0,"Costa Rica":0.7,"Ireland":0.9,"Oman":1.5,"South Sudan":3.0,
    "Burundi":3.5,"Benin":3.2,"Ivory Coast":3.0,
}
DEFAULT_GROWTH = 0.8

# ── Fetch data ────────────────────────────────────────────────────────────────
def fetch_population_data():
    rows, source = [], ""
    try:
        url = "https://restcountries.com/v3.1/all?fields=name,population,region,area,cca2"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        for c in r.json():
            if not isinstance(c, dict): continue
            nf = c.get("name", {})
            if not isinstance(nf, dict): continue
            name = nf.get("common", "")
            pop  = c.get("population", 0)
            if not name or pop < 10000: continue
            rows.append({"country":name,"code":c.get("cca2",""),
                         "population":pop,"region":c.get("region") or "Other",
                         "area_km2":c.get("area") or None})
        if rows: source = "REST Countries API"
    except Exception as e:
        print(f"REST Countries failed: {e}")

    if not rows:
        try:
            url = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=300&mrv=1"
            r = requests.get(url, timeout=15); r.raise_for_status()
            entries = (r.json()[1] or []) if isinstance(r.json(), list) else []
            for e in entries:
                if not isinstance(e, dict): continue
                val  = e.get("value")
                name = (e.get("country") or {}).get("value","")
                if not val or val < 10000 or not name: continue
                rows.append({"country":name,"code":e.get("countryiso3code",""),
                             "population":int(val),
                             "region":COUNTRY_REGIONS.get(name,"Other"),"area_km2":None})
            if rows: source = "World Bank API"
        except Exception as e2:
            print(f"World Bank failed: {e2}")

    if not rows: return pd.DataFrame(), "No data"

    df = pd.DataFrame(rows)
    df["population_m"] = (df["population"]/1_000_000).round(2)
    df["density"]      = (df["population"]/df["area_km2"]).round(1)
    df["growth_rate"]  = df["country"].map(lambda x: COUNTRY_GROWTH.get(x, DEFAULT_GROWTH))
    df.sort_values("population", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["rank"] = df.index + 1
    print(f"✓ {len(df)} countries from {source}")
    return df, source

# ── Constants ─────────────────────────────────────────────────────────────────
EPOCH_MS   = int(datetime.datetime(2025,1,1,tzinfo=datetime.timezone.utc).timestamp()*1000)
INTERVALS  = {"30s":30_000,"1 min":60_000,"5 min":300_000,"15 min":900_000,"Off":None}

# ── App ───────────────────────────────────────────────────────────────────────
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

STYLE = {
    "page":       {"backgroundColor":"#0b0f1a","minHeight":"100vh","fontFamily":"'Inter',sans-serif","color":"#e8eaf0"},
    "header":     {"background":"linear-gradient(135deg,#0b0f1a 0%,#141b2d 100%)","borderBottom":"1px solid #1e2d4a","padding":"24px 32px 20px"},
    "title":      {"fontSize":"28px","fontWeight":"700","color":"#ffffff","letterSpacing":"-0.5px","margin":0},
    "subtitle":   {"fontSize":"13px","color":"#5a6a8a","marginTop":"4px"},
    "stat_card":  {"background":"#111827","border":"1px solid #1e2d4a","borderRadius":"10px","padding":"18px 22px"},
    "stat_num":   {"fontSize":"22px","fontWeight":"700","color":"#38bdf8","fontVariantNumeric":"tabular-nums"},
    "stat_label": {"fontSize":"11px","color":"#5a6a8a","textTransform":"uppercase","letterSpacing":"1px","marginTop":"2px"},
    "card":       {"background":"#111827","border":"1px solid #1e2d4a","borderRadius":"10px","padding":"20px"},
}
CHART_LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter,sans-serif",color="#9aa5b4",size=11),
    margin=dict(t=10,b=10,l=10,r=10),coloraxis_showscale=False)

app.layout = html.Div(style=STYLE["page"], children=[
    html.Link(rel="stylesheet",href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"),

    dcc.Interval(id="counter-ticker",interval=1000,n_intervals=0),
    dcc.Interval(id="auto-refresh",interval=300_000,n_intervals=0,disabled=False),
    dcc.Store(id="data-store"),
    # Stores [{base, rate}, ...] for the currently displayed table rows
    dcc.Store(id="table-tick-store"),

    # Header
    html.Div(style=STYLE["header"],children=[
        dbc.Row([
            dbc.Col([html.H1("🌍 World Population",style=STYLE["title"]),
                     html.Div(id="last-updated",style=STYLE["subtitle"])],width=7),
            dbc.Col(dbc.Row([
                dbc.Col(html.Div([
                    html.Label("Auto-refresh",style={"fontSize":"11px","color":"#5a6a8a","display":"block","marginBottom":"4px"}),
                    dcc.Dropdown(id="interval-picker",
                                 options=[{"label":k,"value":k} for k in INTERVALS],
                                 value="5 min",clearable=False,
                                 style={"backgroundColor":"#1a2235","color":"#000","fontSize":"13px"}),
                ]),width=7),
                dbc.Col(dbc.Button("↻ Now",id="refresh-btn",n_clicks=0,size="sm",
                    style={"backgroundColor":"#1d4ed8","border":"none","marginTop":"20px","width":"100%"}),width=5),
            ]),width=5),
        ])
    ]),

    html.Div(style={"padding":"24px 32px"},children=[
        # Stat cards
        dbc.Row(style={"marginBottom":"20px"},children=[
            dbc.Col(html.Div(style=STYLE["stat_card"],children=[
                html.Div(id="live-pop-counter",style=STYLE["stat_num"]),
                html.Div("World Population · Live",style=STYLE["stat_label"]),
            ]),width=3),
            dbc.Col(html.Div(style=STYLE["stat_card"],children=[
                html.Div(id="stat-countries",style=STYLE["stat_num"]),
                html.Div("Countries Tracked",style=STYLE["stat_label"]),
            ]),width=3),
            dbc.Col(html.Div(style=STYLE["stat_card"],children=[
                html.Div(id="stat-top",style=STYLE["stat_num"]),
                html.Div("Most Populous Country",style=STYLE["stat_label"]),
            ]),width=3),
            dbc.Col(html.Div(style=STYLE["stat_card"],children=[
                html.Div(id="stat-region",style=STYLE["stat_num"]),
                html.Div("Largest Region",style=STYLE["stat_label"]),
            ]),width=3),
        ]),

        # Controls
        dbc.Row(style={"marginBottom":"16px"},children=[
            dbc.Col([
                html.Label("Region",style={"fontSize":"11px","color":"#5a6a8a","textTransform":"uppercase","letterSpacing":"1px","marginBottom":"6px"}),
                dcc.Dropdown(id="region-filter",options=[],value="All",clearable=False,
                             style={"backgroundColor":"#1a2235","color":"#000"}),
            ],width=3),
            dbc.Col([
                html.Label("Chart Type",style={"fontSize":"11px","color":"#5a6a8a","textTransform":"uppercase","letterSpacing":"1px","marginBottom":"6px"}),
                dcc.Dropdown(id="chart-type",
                    options=[{"label":"Bar Chart – Top Countries","value":"bar"},
                             {"label":"Treemap – by Region","value":"treemap"},
                             {"label":"World Map","value":"map"},
                             {"label":"Region Breakdown (Pie)","value":"pie"}],
                    value="bar",clearable=False,style={"backgroundColor":"#1a2235","color":"#000"}),
            ],width=4),
            dbc.Col([
                html.Label("Top N Countries",style={"fontSize":"11px","color":"#5a6a8a","textTransform":"uppercase","letterSpacing":"1px","marginBottom":"6px"}),
                dcc.Slider(id="top-n",min=10,max=50,step=5,value=20,
                           marks={i:str(i) for i in [10,20,30,40,50]},tooltip={"placement":"bottom"}),
            ],width=5),
        ]),

        # Charts
        dbc.Row(style={"marginBottom":"20px"},children=[
            dbc.Col(html.Div(style=STYLE["card"],children=[
                dcc.Graph(id="main-chart",style={"height":"420px"},config={"displayModeBar":False}),
            ]),width=8),
            dbc.Col(html.Div(style=STYLE["card"],children=[
                dcc.Graph(id="region-chart",style={"height":"420px"},config={"displayModeBar":False}),
            ]),width=4),
        ]),

        # Table
        dbc.Row([dbc.Col(html.Div(style=STYLE["card"],children=[
            html.Div("Country Rankings",style={"fontSize":"13px","fontWeight":"600","color":"#9aa5b4",
                                               "textTransform":"uppercase","letterSpacing":"1px","marginBottom":"14px"}),
            html.Div(id="data-table",style={"overflowX":"auto"}),
        ]))]),
    ]),
])

# ── World counter (clientside) ────────────────────────────────────────────────
app.clientside_callback(
    f"""
    function(n) {{
        var elapsed = (Date.now() - {EPOCH_MS}) / 1000;
        return Math.round(8092000000 + elapsed * 2.3).toLocaleString('en-US');
    }}
    """,
    Output("live-pop-counter","children"),
    Input("counter-ticker","n_intervals"),
)

# ── Table ticker (clientside) — reads from table-tick-store ──────────────────
app.clientside_callback(
    f"""
    function(n, tickData) {{
        if (!tickData || !tickData.rows) return window.dash_clientside.no_update;
        var elapsed = (Date.now() - {EPOCH_MS}) / 1000;
        var rows = tickData.rows;
        rows.forEach(function(r, i) {{
            var el = document.getElementById('pop-cell-' + i);
            if (el) {{
                var val = Math.round(r.base + elapsed * r.rate);
                el.textContent = val.toLocaleString('en-US');
            }}
        }});
        return window.dash_clientside.no_update;
    }}
    """,
    Output("table-tick-store","modified_timestamp"),
    Input("counter-ticker","n_intervals"),
    State("table-tick-store","data"),
)

# ── Server callbacks ──────────────────────────────────────────────────────────
@callback(Output("auto-refresh","interval"),Output("auto-refresh","disabled"),
          Input("interval-picker","value"))
def set_interval(v):
    ms = INTERVALS.get(v)
    return (300_000,True) if ms is None else (ms,False)

@callback(Output("data-store","data"),
          Input("auto-refresh","n_intervals"),Input("refresh-btn","n_clicks"))
def refresh_data(_i,_c):
    df,source = fetch_population_data()
    if df.empty: return json.dumps({"rows":[],"source":"No data","fetched_at":""})
    return json.dumps({"rows":df.to_dict("records"),"source":source,
                       "fetched_at":datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S")})

@callback(Output("region-filter","options"),Output("region-filter","value"),
          Input("data-store","data"),State("region-filter","value"))
def update_regions(sj,cur):
    if not sj: return [{"label":"All","value":"All"}],"All"
    df = pd.DataFrame(json.loads(sj)["rows"])
    if df.empty: return [{"label":"All","value":"All"}],"All"
    regions = ["All"]+sorted(df["region"].dropna().unique().tolist())
    return [{"label":r,"value":r} for r in regions],(cur if cur in regions else "All")

@callback(Output("stat-countries","children"),Output("stat-top","children"),
          Output("stat-region","children"),Output("last-updated","children"),
          Input("data-store","data"))
def update_stats(sj):
    if not sj: return "—","—","—","Loading…"
    s  = json.loads(sj); df = pd.DataFrame(s["rows"])
    if df.empty: return "0","N/A","N/A","No data"
    return (f"{len(df):,}", df.iloc[0]["country"],
            df.groupby("region")["population"].sum().idxmax(),
            f"Source: {s['source']} · Updated {s['fetched_at']}")

@callback(Output("main-chart","figure"),
          Input("data-store","data"),Input("region-filter","value"),
          Input("chart-type","value"),Input("top-n","value"))
def update_main_chart(sj,region,chart_type,top_n):
    if not sj: return go.Figure()
    df = pd.DataFrame(json.loads(sj)["rows"])
    if df.empty: return go.Figure()
    f = df if region=="All" else df[df["region"]==region]
    if f.empty: return go.Figure()
    if chart_type=="bar":
        fig=px.bar(f.head(top_n),x="population_m",y="country",orientation="h",
                   color="population_m",color_continuous_scale="Blues",
                   labels={"population_m":"Population (M)","country":""},custom_data=["region","rank"])
        fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x:.1f}M<br>Region: %{customdata[0]}<br>Rank: #%{customdata[1]}<extra></extra>")
        fig.update_layout(**CHART_LAYOUT,yaxis=dict(autorange="reversed",tickfont=dict(size=10)),
                          xaxis=dict(showgrid=True,gridcolor="#1e2d4a"))
    elif chart_type=="treemap":
        fig=px.treemap(f,path=["region","country"],values="population",
                       color="population",color_continuous_scale="Blues")
        fig.update_traces(hovertemplate="<b>%{label}</b><br>%{value:,.0f}<extra></extra>")
        fig.update_layout(**CHART_LAYOUT)
    elif chart_type=="map":
        fig=px.choropleth(f,locations="code",color="population_m",hover_name="country",
                          color_continuous_scale="Blues",labels={"population_m":"Population (M)"})
        fig.update_layout(**CHART_LAYOUT,geo=dict(bgcolor="rgba(0,0,0,0)",showframe=False,
                          showcoastlines=True,coastlinecolor="#1e2d4a",
                          landcolor="#1a2235",oceancolor="#0b0f1a",showocean=True))
    elif chart_type=="pie":
        rd=f.groupby("region")["population"].sum().reset_index()
        fig=px.pie(rd,names="region",values="population",
                   color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_traces(textinfo="label+percent",hovertemplate="<b>%{label}</b><br>%{value:,.0f}<extra></extra>")
        fig.update_layout(**CHART_LAYOUT)
    else: fig=go.Figure()
    return fig

@callback(Output("region-chart","figure"),
          Input("data-store","data"),Input("region-filter","value"))
def update_region_chart(sj,region):
    if not sj: return go.Figure()
    df=pd.DataFrame(json.loads(sj)["rows"])
    if df.empty: return go.Figure()
    rt=df.groupby("region")["population"].sum().reset_index()
    rt["population_b"]=(rt["population"]/1e9).round(2)
    rt.sort_values("population",ascending=True,inplace=True)
    colors=["#38bdf8" if (region!="All" and r==region) else "#1d4ed8" for r in rt["region"]]
    fig=go.Figure(go.Bar(x=rt["population_b"],y=rt["region"],orientation="h",marker_color=colors,
                         hovertemplate="<b>%{y}</b><br>%{x:.2f}B<extra></extra>"))
    fig.update_layout(**CHART_LAYOUT,xaxis=dict(title="Population (B)",showgrid=True,gridcolor="#1e2d4a"),
                      yaxis=dict(tickfont=dict(size=10)),
                      title=dict(text="By Region",font=dict(size=12,color="#9aa5b4"),x=0))
    return fig

@callback(
    Output("data-table","children"),
    Output("table-tick-store","data"),
    Input("data-store","data"),
    Input("region-filter","value"),
    Input("top-n","value"),
)
def update_table(sj,region,top_n):
    if not sj: return html.Div("Loading…",style={"color":"#5a6a8a"}), None
    df=pd.DataFrame(json.loads(sj)["rows"])
    if df.empty: return html.Div("No data.",style={"color":"#5a6a8a"}), None
    filtered=df if region=="All" else df[df["region"]==region]
    data=filtered.head(top_n).copy()

    hdr={"backgroundColor":"#0b0f1a","color":"#5a6a8a","fontSize":"11px",
         "textTransform":"uppercase","letterSpacing":"1px","padding":"8px 14px",
         "borderBottom":"1px solid #1e2d4a","textAlign":"left"}
    td ={"padding":"8px 14px","borderBottom":"1px solid #1a2235","color":"#c8d0dc","fontSize":"13px"}
    td_pop={**td,"color":"#38bdf8","fontWeight":"600","fontVariantNumeric":"tabular-nums"}

    tick_rows = []
    header=html.Tr([html.Th(c,style=hdr) for c in ["#","Country","Region","Population (live)","Growth/sec"]])
    rows=[]
    for i,(_,row) in enumerate(data.iterrows()):
        bg={"backgroundColor":"#0f172a"} if i%2==0 else {"backgroundColor":"#111827"}
        pop=int(row["population"])
        rate=float(row.get("growth_rate", DEFAULT_GROWTH))
        tick_rows.append({"base": pop, "rate": rate})
        rate_color="#34d399" if rate>=0 else "#f87171"
        rate_label=f"+{rate:.2f}/s" if rate>=0 else f"{rate:.2f}/s"
        rows.append(html.Tr([
            html.Td(f"#{int(row['rank'])}",style={**td,**bg,"color":"#5a6a8a"}),
            html.Td(row["country"],         style={**td,**bg,"fontWeight":"500","color":"#e8eaf0"}),
            html.Td(row["region"],          style={**td,**bg}),
            # id="pop-cell-{i}" is what the clientside callback targets
            html.Td(f"{pop:,}", id=f"pop-cell-{i}", style={**td_pop,**bg}),
            html.Td(rate_label,             style={**td,**bg,"color":rate_color,"fontSize":"12px"}),
        ]))

    table=html.Table([html.Thead(header),html.Tbody(rows)],
                     style={"width":"100%","borderCollapse":"collapse"})
    return table, {"rows": tick_rows}

if __name__ == "__main__":
    app.run(debug=True)
