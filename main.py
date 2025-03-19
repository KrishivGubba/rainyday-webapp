import streamlit as st
import os
import json

st.set_page_config(page_title="RainyDay Configuration", layout="wide")

st.title("RainyDay Configuration App")
st.markdown("This app helps you create a configuration file for RainyDay. Fill in the fields below and click 'Generate Configuration' to create your config file.")

with st.form("rainy_day_config"):
    st.header("Basic Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        main_path = st.file_uploader("Main path", type=None, help="Directory where the control file is located and in which subdirectories will be created or modified.")
        scenario_name = st.file_uploader("Scenario Name", help="Name for the scenario. This will be the name of the subdirectory and the prefix for various output")
        rain_path = st.text_input("RAINPATH", help="The location of the rainfall input NetCDF4 files. Only needed if creating a new storm catalog")
        catalog_name = st.text_input("CATALOGNAME", help="The name of the storm catalog")
    
    with col2:
        create_catalog = st.selectbox(
            "Create Catalog?", 
            options=["true", "false"], 
            help="True: create new catalog, False: use existing"
        )
        duration = st.number_input("Duration", min_value=1, help="Duration of the rainfall accumulation period in hours", value=24)
        duration_correction = st.selectbox(
            "Duration Correction?", 
            options=["true", "false"], 
            help="Recommended if generating IDF curves, particularly if they are of relatively short duration"
        )
        n_storms = st.number_input("NSTORMS", min_value=1, help="How many storms to include in the storm catalog or analysis", value=20)
    
    st.header("Analysis Configuration")
    
    col3, col4 = st.columns(2)
    
    with col3:
        n_years = st.number_input("Number of Years", min_value=1, help="How many years of annual maxima rainfall to be synthesized", value=100)
        n_realizations = st.number_input("Number of Realizations", min_value=1, help="How many NYEARS-long sequences to be generated", value=1)
        uncertainty = st.text_input("Uncertainty", value="ensemble", help="Defines the type of uncertainty to calculate ('ensemble' or a positive integer)")
        time_separation = st.number_input("TIMESEPARATION", min_value=0, help="The minimum separation time in hours between two storms", value=0)
    
    with col4:
        domain_type = st.selectbox(
            "DOMAINTYPE", 
            options=["rectangular", "irregular"], 
            help="Type of domain: 'rectangular' or 'irregular'"
        )
        
        if domain_type == "rectangular":
            st.subheader("Rectangular Domain Settings")
            latitude_min = st.number_input("LATITUDE_MIN", help="Southern boundary of transposition domain", value=42.5)
            latitude_max = st.number_input("LATITUDE_MAX", help="Northern boundary of transposition domain", value=44.0)
            longitude_min = st.number_input("LONGITUDE_MIN", help="Western boundary of transposition domain", value=-90.5)
            longitude_max = st.number_input("LONGITUDE_MAX", help="Eastern boundary of transposition domain", value=-88.0)
        else:
            st.subheader("Irregular Domain Settings")
            domain_shp = st.text_input("DOMAINSHP", help="File path for RainyDay-compliant shapefile defining the boundary")
            
    st.header("Output and Analysis Options")
    
    col5, col6 = st.columns(2)
    
    with col5:
        diagnostic_plots = st.selectbox(
            "DIAGNOSTICPLOTS", 
            options=["true", "false"], 
            help="Set to 'true' to produce diagnostic plots"
        )
        freq_analysis = st.selectbox(
            "FREQANALYSIS", 
            options=["true", "false"], 
            help="Create a '.FreqAnalysis' file based on the rainfall annual maxima generated"
        )
        scenarios = st.selectbox(
            "SCENARIOS", 
            options=["false", "true"], 
            help="Create watershed-specific spacetime rainfall scenarios"
        )
        
    with col6:
        spin_period = st.text_input("SPINPERIOD", value="false", help="'false' or integer number of days to prepend rainfall period")
        return_threshold = st.number_input("RETURNTHRESHOLD", min_value=1, help="Minimum return period for scenarios", value=1)
        
        exclude_storms_type = st.selectbox(
            "Exclude Storms Type", 
            options=["None", "Range", "List"],
            help="How to specify storms to exclude"
        )
        
        if exclude_storms_type == "None":
            exclude_storms = "none"
        elif exclude_storms_type == "Range":
            exclude_storms_min = st.number_input("Exclude Storms Min", min_value=1, value=1)
            exclude_storms_max = st.number_input("Exclude Storms Max", min_value=1, value=200)
            exclude_storms = f"{exclude_storms_min}-{exclude_storms_max}"
        elif exclude_storms_type == "List":
            exclude_storms_input = st.text_input("EXCLUDESTORMS (comma-separated)", value="")
            exclude_storms = f"[{exclude_storms_input}]" if exclude_storms_input else "none"
    
    st.header("Advanced Configuration")
    
    col7, col8 = st.columns(2)
    
    with col7:
        exclude_months_type = st.selectbox(
            "Exclude Months Type", 
            options=["None", "Range", "List"],
            help="How to specify months to exclude"
        )
        
        if exclude_months_type == "None":
            exclude_months = "none"
        elif exclude_months_type == "Range":
            exclude_months_min = st.number_input("Exclude Months Min", min_value=1, max_value=12, value=1)
            exclude_months_max = st.number_input("Exclude Months Max", min_value=1, max_value=12, value=3)
            exclude_months = f"{exclude_months_min}-{exclude_months_max}"
        elif exclude_months_type == "List":
            exclude_months_input = st.text_input("EXCLUDEMONTHS (comma-separated)", value="")
            exclude_months = f"[{exclude_months_input}]" if exclude_months_input else "none"
            
        include_years_type = st.selectbox(
            "Include Years Type", 
            options=["All", "Range", "List"],
            help="How to specify years to include"
        )
        
        if include_years_type == "All":
            include_years = "all"
        elif include_years_type == "Range":
            include_years_min = st.number_input("Include Years Min", min_value=1900, max_value=2100, value=2002)
            include_years_max = st.number_input("Include Years Max", min_value=1900, max_value=2100, value=2021)
            include_years = f"{include_years_min}-{include_years_max}"
        elif include_years_type == "List":
            include_years_input = st.text_input("INCLUDEYEARS (comma-separated)", value="")
            include_years = f"[{include_years_input}]" if include_years_input else "all"
            
    with col8:
        resampling = st.selectbox(
            "RESAMPLING", 
            options=["poisson", "empirical", "negbinom"], 
            help="Method for generating the number of storms"
        )
        
        transposition = st.selectbox(
            "TRANSPOSITION", 
            options=["uniform", "nonuniform"], 
            help="How the random spatial transposition should be done"
        )
        
        rotation_type = st.selectbox(
            "Rotation Angle Type",
            options=["None", "Custom"],
            help="Whether to enable storm rotation"
        )
        
        if rotation_type == "None":
            rotation_angle = "none"
        else:
            rotation_min = st.number_input("Min Angle", max_value=0, value=-20)
            rotation_max = st.number_input("Max Angle", min_value=0, value=20)
            rotation_n = st.number_input("N Angles", min_value=1, value=5)
            rotation_angle = f"{rotation_min},{rotation_max},{rotation_n}"
            
        return_levels = st.text_input("RETURNLEVELS (comma-separated)", value="2,5,10,20,50,100,200,500,1000")
        
    st.header("Area Configuration")
    
    # if "showOpt" not in st.session_state:
    #     st.session_state = False

    point_area = st.selectbox(
        "POINTAREA", 
        options=["point", "grid", "rectangle", "watershed"], 
        help="Defines the area that will be used in rainfall calculations"
    )

    if point_area in ["point", "grid"]:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            point_lat = st.number_input("POINTLAT", help="The latitude of the analysis point")
        with col_p2:
            point_lon = st.number_input("POINTLON", help="The longitude of the analysis point")
    elif point_area == "rectangle":
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            box_y_min = st.number_input("BOX_YMIN", help="Southernmost boundary of the analysis box")
            box_y_max = st.number_input("BOX_YMAX", help="Northernmost boundary of the analysis box")
        with col_b2:
            box_x_min = st.number_input("BOX_XMIN", help="Westernmost boundary of the analysis box")
            box_x_max = st.number_input("BOX_XMAX", help="Easternmost boundary of the analysis box")
    elif point_area == "watershed":
        watershed_shp = st.text_input("WATERSHEDSHP", help="File path for RainyDay-compliant shapefile defining the watershed boundary")
        
    st.header("Sensitivity and Calculation Options")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        sens_intensity = st.text_input("SENS_INTENSITY", value="false", help="'false' or decimal percentage change to rainfall intensity")
        sens_frequency = st.text_input("SENS_FREQUENCY", value="false", help="'false' or decimal percentage change to storm occurrence rate")
    
    with col_s2:
        calc_type = st.selectbox(
            "CALCTYPE", 
            options=["ams", "pds"], 
            help="Type of analysis: 'ams'/'annmax' or 'pds'/'partialduration'"
        )
        
        n_per_year = st.text_input("NPERYEAR", value="false", help="'false' or positive integer for multiple rainstorms per year")
        
        max_transpo = st.selectbox(
            "Max Transposition", 
            options=["false", "true"], 
            help="If 'true', find the specific transposition that maximizes precipitation"
        )
        
    # Submit button
    submitted = st.form_submit_button("Generate Configuration")
    
    if submitted:
        if not main_path or not scenario_name or not rain_path:
            st.error("Fields missing")
        else:
            print(main_path, "this is the main path")
            config = {
                "MAINPATH": main_path.name,
                "SCENARIONAME": scenario_name.name,
                "RAINPATH": rain_path,
                "CATALOGNAME": catalog_name,
                "CREATECATALOG": create_catalog,
                "DURATION": duration,
                "DURATIONCORRECTION": duration_correction,
                "NSTORMS": n_storms,
                "NYEARS": n_years,
                "NREALIZATIONS": n_realizations,
                "UNCERTAINTY": uncertainty,
                "TIMESEPARATION": time_separation,
                "DOMAINTYPE": domain_type,
                "DIAGNOSTICPLOTS": diagnostic_plots,
                "FREQANALYSIS": freq_analysis,
                "SCENARIOS": scenarios,
                "SPINPERIOD": spin_period,
                "RETURNTHRESHOLD": return_threshold,
                "EXCLUDESTORMS": exclude_storms,
                "EXCLUDEMONTHS": exclude_months,
                "INCLUDEYEARS": include_years,
                "RESAMPLING": resampling,
                "TRANSPOSITION": transposition,
                "ROTATIONANGLE": rotation_angle,
                "RETURNLEVELS": return_levels,
                "POINTAREA": point_area,
                "SENS_INTENSITY": sens_intensity,
                "SENS_FREQUENCY": sens_frequency,
                "CALCTYPE": calc_type,
                "NPERYEAR": n_per_year,
                "MAXTRANSPO": max_transpo
            }
            
            # Add domain-specific fields
            if domain_type == "rectangular":
                config["AREAEXTENT"] = {
                    "LATITUDE_MIN": latitude_min,
                    "LATITUDE_MAX": latitude_max,
                    "LONGITUDE_MIN": longitude_min,
                    "LONGITUDE_MAX": longitude_max
                }
            else:
                config["DOMAINSHP"] = domain_shp
                
            # Add point area specific fields
            if point_area in ["point", "grid"]:
                config["POINTLAT"] = point_lat
                config["POINTLON"] = point_lon
            elif point_area == "rectangle":
                config["BOX_YMIN"] = box_y_min
                config["BOX_YMAX"] = box_y_max
                config["BOX_XMIN"] = box_x_min
                config["BOX_XMAX"] = box_x_max
            elif point_area == "watershed":
                config["WATERSHEDSHP"] = watershed_shp
                
            # Convert to JSON
            config_json = json.dumps(config, indent=4)
            
            # Display the configuration
            st.subheader("Generated Configuration")
            st.code(config_json, language="json")
            