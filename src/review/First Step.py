# -*- coding: utf-8 -*-
"""
Generated by ArcGIS ModelBuilder on : 2025-06-10 11:32:45
"""
import arcpy

def Refresh():  # First Step
    """ArcPy model step: pull data and buffer features."""

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = False

    arcpy.ImportToolbox(r"c:\program files\arcgis\pro\Resources\ArcToolbox\toolboxes\Data Management Tools.tbx")
    arcpy.ImportToolbox(r"D:\ArcGIS\Projects\Street_Tree_Planting_Analysis\Street_Tree_Planting_Analysis_Python.atbx")
    # Model Environment settings
    with arcpy.EnvManager(scratchWorkspace="D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Scrap.gdb", workspace="D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Scrap.gdb"):
        Online_NYZD = "https:\\\\services5.arcgis.com\\GfwWNkhOj9bNBqoJ\\arcgis\\rest\\services\\nyzd\\FeatureServer\\0"
        Query = "ZONEDIST LIKE 'M1%' Or ZONEDIST LIKE 'M2%' Or ZONEDIST LIKE 'M3%'"
        BK_Vaults = "D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp"
        STP_Apps_Vaults = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DOT_Vault"
        FHNR_Apps_STSURVEY_ConEd_Transformer_Vault = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.ConEd_Transformer_Vault"
        FHNR_Apps_STSURVEY_DEP_GI_Assets = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets"
        SIDEWALK = "D:\\ArcGIS\\Data\\FileGDB-data-Planimetric_2022_AGOL_Link.gdb\\SIDEWALK"
        FHNR_Datasets_FHNR_HVI_CensusTracts_v2013 = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\SQLServer-data-FHNR_Datasets.sde\\FHNR_Datasets.FHNR.HVI_CensusTracts_v2013"
        Curb_Cuts_Intersections_2_ = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Data.gdb\\Curb_Cuts_Intersections"
        Subway_Lines = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Subway_Lines"
        Workorders_csv = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Excel\\Workorders.csv"
        TreeandSite_csv = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Excel\\TreeandSite.csv"
        Grass_Shrub_ExportFeatures = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Scrap.gdb\\Grass_Shrub_ExportFeatures"
        Political_Boundary = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Political_Boundary"
        FHNR_Datasets_FHNR_HVI_CensusTracts_v2013_2_ = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\SQLServer-data-FHNR_Datasets.sde\\FHNR_Datasets.FHNR.HVI_CensusTracts_v2013"
        NYCDOHMH_HVI_CensusTracts_2018_Clip = "D:\\ArcGIS\\GDBs\\FileGDB-data-NYC_Parks_Pre_Union_Mashup.gdb\\NYCDOHMH_HVI_CensusTracts_2018_Clip"
        NYCDOHMH_HVI_CensusTracts_2023 = "D:\\ArcGIS\\GDBs\\FileGDB-data-NYC_Parks_Pre_Union_Mashup.gdb\\NYCDOHMH_HVI_CensusTracts_2023"
        NYCDOHMH_HVI_NeighborhoodTabulationAreas_2018 = "D:\\ArcGIS\\GDBs\\FileGDB-data-NYC_Parks_Pre_Union_Mashup.gdb\\NYCDOHMH_HVI_NeighborhoodTabulationAreas_2018"
        NYCDOHMH_HVI_NeighborhoodTabulationAreas_2023 = "D:\\ArcGIS\\GDBs\\FileGDB-data-NYC_Parks_Pre_Union_Mashup.gdb\\NYCDOHMH_HVI_NeighborhoodTabulationAreas_2023"
        NYCDCP_Borough_Boundaries_Water_Included = "D:\\ArcGIS\\GDBs\\FileGDB-data-NYC_Parks_Pre_Union_Mashup.gdb\\NYCDCP_Borough_Boundaries_Water_Included"
        NYCDCP_Borough_Boundaries = "D:\\ArcGIS\\GDBs\\FileGDB-data-NYC_Parks_Pre_Union_Mashup.gdb\\NYCDCP_Borough_Boundaries"
        Street_Centerline = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Street_Centerline"
        DEP_Hydrants = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\DEP_Hydrants"
        Sidewalk_Pluto = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Street_Tree_Planting_Analysis.gdb\\Sidewalk_Pluto"
        BK_Vaults_Buffer_2_ = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\BK_Vaults_Buffer"
        DOT_Vault_Buffer_2_ = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\DOT_Vault_Buffer"

        # Process: Export Features (Export Features) (conversion)
        NYZD = fr"{arcpy.env.scratchGDB}\NYZD"
        arcpy.conversion.ExportFeatures(in_features=Online_NYZD, out_features=NYZD, where_clause=Query, field_mapping="ZONEDIST \"ZONEDIST\" true true false 15 Text 0 0,First,#,https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyzd/FeatureServer/0,ZONEDIST,0,14;Shape__Area \"Shape__Area\" false true true 0 Double 0 0,First,#,https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyzd/FeatureServer/0,Shape__Area,-1,-1;Shape__Length \"Shape__Length\" false true true 0 Double 0 0,First,#,https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyzd/FeatureServer/0,Shape__Length,-1,-1")

        # Process: Pairwise Buffer: 20ft per NYZD (Pairwise Buffer) (analysis)
        NYZD_Buffer = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\NYZD_Buffer"
        arcpy.analysis.PairwiseBuffer(in_features=NYZD, out_feature_class=NYZD_Buffer, buffer_distance_or_field="20 Feet", dissolve_option="NONE")

        # Process: Export Features (2) (Export Features) (conversion)
        BK_Vaults_2_ = fr"{arcpy.env.scratchGDB}\BK_Vaults"
        arcpy.conversion.ExportFeatures(in_features=BK_Vaults, out_features=BK_Vaults_2_, field_mapping="OBJECTID \"OBJECTID\" true true false 10 Long 0 10,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,OBJECTID,-1,-1;Shape_Leng \"Shape_Leng\" true true false 19 Double 0 0,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,Shape_Leng,-1,-1;Shape_Area \"Shape_Area\" true true false 19 Double 0 0,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,Shape_Area,-1,-1;OID_ \"OID_\" true true false 10 Long 0 10,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,OID_,-1,-1;Rec_Num \"Rec_Num\" true true false 10 Long 0 10,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,Rec_Num,-1,-1;Boro \"Boro\" true true false 10 Long 0 10,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,Boro,-1,-1;BLCK \"BLCK\" true true false 50 Text 0 0,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,BLCK,0,49;Lot \"Lot\" true true false 50 Text 0 0,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,Lot,0,49;Dimensions \"Dimensions\" true true false 100 Text 0 0,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,Dimensions,0,99;Num_Vaults \"Num_Vaults\" true true false 10 Long 0 10,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,Num_Vaults,-1,-1;Location \"Location\" true true false 254 Text 0 0,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,Location,0,253;Data \"Data\" true true false 254 Text 0 0,First,#,D:\\ArcGIS\\Data\\Vaults\\BK_Vaults.shp,Data,0,253")

        # Process: Pairwise Buffer: 20ft per BK Vault (Pairwise Buffer) (analysis)
        BK_Vaults_Buffer = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\BK_Vaults_Buffer"
        arcpy.analysis.PairwiseBuffer(in_features=BK_Vaults_2_, out_feature_class=BK_Vaults_Buffer, buffer_distance_or_field="20 Feet", dissolve_option="NONE")

        # Process: Export Features (3) (Export Features) (conversion)
        STP_Vaults = fr"{arcpy.env.scratchGDB}\DOT_Vault_ExportFeatures"
        arcpy.conversion.ExportFeatures(in_features=STP_Apps_Vaults, out_features=STP_Vaults, field_mapping="BL_Junk_CD \"CD\" true true false 4 Long 0 10,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DOT_Vault,BL_Junk_CD,-1,-1;BL_Junk_CB \"CB\" true true false 5 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DOT_Vault,BL_Junk_CB,0,4;BL_Junk_Zi \"Zip Code\" true true false 4 Long 0 10,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DOT_Vault,BL_Junk_Zi,-1,-1;BL_Junk_Ad \"Address\" true true false 28 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DOT_Vault,BL_Junk_Ad,0,27;BL_Junk__9 \"BL_Junk_9\" true true false 21 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DOT_Vault,BL_Junk__9,0,20;Junk_LOCAT \"Location\" true true false 254 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DOT_Vault,Junk_LOCAT,0,253;GlobalID \"GlobalID\" false false true 38 GlobalID 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DOT_Vault,GlobalID,-1,-1;STArea() \"STArea()\" false true true 0 Double 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DOT_Vault,STArea(),-1,-1;STLength() \"STLength()\" false true true 0 Double 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DOT_Vault,STLength(),-1,-1")

        # Process: Pairwise Buffer: 20ft per MN Vault (Pairwise Buffer) (analysis)
        DOT_Vault_Buffer = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\DOT_Vault_Buffer"
        arcpy.analysis.PairwiseBuffer(in_features=STP_Vaults, out_feature_class=DOT_Vault_Buffer, buffer_distance_or_field="20 Feet", dissolve_option="NONE")

        # Process: Export Features (4) (Export Features) (conversion)
        ConEd_Transformer_Vault_3_ = fr"{arcpy.env.scratchGDB}\ConEd_Transformer_Vault"
        arcpy.conversion.ExportFeatures(in_features=FHNR_Apps_STSURVEY_ConEd_Transformer_Vault, out_features=ConEd_Transformer_Vault_3_, field_mapping="ASSET_TAG \"ASSET_TAG\" true true false 254 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.ConEd_Transformer_Vault,ASSET_TAG,0,253;DIRECT_ADD \"DIRECT_ADD\" true true false 254 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.ConEd_Transformer_Vault,DIRECT_ADD,0,253;BOROUGH \"BOROUGH\" true true false 254 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.ConEd_Transformer_Vault,BOROUGH,0,253;FLTY_FACIL \"FLTY_FACIL\" true true false 254 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.ConEd_Transformer_Vault,FLTY_FACIL,0,253;GlobalID \"GlobalID\" false false true 38 GlobalID 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.ConEd_Transformer_Vault,GlobalID,-1,-1")

        # Process: Pairwise Buffer: 20ft Per ConED Transformer (Pairwise Buffer) (analysis)
        ConEd_Transformer_Buffer = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\ConEd_Transformer_Buffer"
        arcpy.analysis.PairwiseBuffer(in_features=ConEd_Transformer_Vault_3_, out_feature_class=ConEd_Transformer_Buffer, buffer_distance_or_field="20 Feet", dissolve_option="NONE")

        # Process: Export Features (5) (Export Features) (conversion)
        DEP_GI_Assets_2_ = fr"{arcpy.env.scratchGDB}\DEP_GI_Assets"
        arcpy.conversion.ExportFeatures(in_features=FHNR_Apps_STSURVEY_DEP_GI_Assets, out_features=DEP_GI_Assets_2_, field_mapping="Asset_ID \"Asset ID\" true true false 4 Long 0 10,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Asset_ID,-1,-1;GI_ID \"GI ID\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,GI_ID,0,254;DEP_Contract_No_ \"DEP Contract No.\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,DEP_Contract_No_,0,254;DEP_Contract_Phase \"DEP Contract Phase\" true true false 4 Long 0 10,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,DEP_Contract_Phase,-1,-1;Row_Onsite \"Row/Onsite\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Row_Onsite,0,254;Project_Name \"Project Name\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Project_Name,0,254;Asset_Type \"Asset Type\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Asset_Type,0,254;Status \"Status\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Status,0,254;Borough \"Borough\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Borough,0,254;Sewer_Type \"Sewer Type\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Sewer_Type,0,254;Outfall \"Outfall\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Outfall,0,254;NYC_Watershed \"NYC Watershed\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,NYC_Watershed,0,254;BBL \"BBL\" true true false 8 Double 8 38,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,BBL,-1,-1;Secondary_BBL \"Secondary BBL\" true true false 8 Double 8 38,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Secondary_BBL,0,254;Community_Board \"Community Board\" true true false 4 Long 0 10,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Community_Board,-1,-1;City_Council \"City Council\" true true false 4 Long 0 10,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,City_Council,-1,-1;Assembly_District \"Assembly District\" true true false 4 Long 0 10,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Assembly_District,-1,-1;Asset_Length__ft_ \"Asset Length (ft)\" true true false 4 Long 0 10,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Asset_Length__ft_,-1,-1;Asset_Width__ft_ \"Asset Width (ft)\" true true false 8 Double 8 38,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Asset_Width__ft_,-1,-1;Asset_Area \"Asset Area\" true true false 8 Double 8 38,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Asset_Area,-1,-1;GI_Feature \"GI Feature\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,GI_Feature,0,254;Tree_Latin_Name_with_Cultivar \"Tree Latin Name with Cultivar\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Tree_Latin_Name_with_Cultivar,0,254;Tree_Common_Name \"Tree Common Name\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Tree_Common_Name,0,254;Construction_Contract_No \"Construction Contract No\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Construction_Contract_No,0,1073741821;Construction_Stage \"Construction Stage\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Construction_Stage,0,1073741821;Program_Areas \"Program Areas\" true true false 1073741822 Text 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,Program_Areas,0,254;GlobalID \"GlobalID\" false false true 38 GlobalID 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\SQLServer-data-FHNR_Apps.sde\\FHNR_Apps.STSURVEY.DEP_GI_Assets,GlobalID,-1,-1")

        # Process: Pairwise Buffer: 20ft Per GI Asset (Pairwise Buffer) (analysis)
        DEP_GI_Assets_Buffer = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\DEP_GI_Assets_Buffer"
        arcpy.analysis.PairwiseBuffer(in_features=DEP_GI_Assets_2_, out_feature_class=DEP_GI_Assets_Buffer, buffer_distance_or_field="20 Feet", dissolve_option="NONE")

        # Process: Copy Features (2) (Copy Features) (management)
        SIDEWALK_2_ = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\SIDEWALK"
        arcpy.management.CopyFeatures(in_features=SIDEWALK, out_feature_class=SIDEWALK_2_)

        # Process: Copy Features (3) (Copy Features) (management)
        HVI_CensusTracts_v2013_Copy_shp = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\HVI_CensusTracts_v2013_Copy.shp"
        arcpy.management.CopyFeatures(in_features=FHNR_Datasets_FHNR_HVI_CensusTracts_v2013, out_feature_class=HVI_CensusTracts_v2013_Copy_shp)

        # Process: Copy Features (4) (Copy Features) (management)
        CURB_CUT_CopyFeatures = fr"{arcpy.env.scratchGDB}\CURB_CUT_CopyFeatures"
        arcpy.management.CopyFeatures(in_features=Curb_Cuts_Intersections_2_, out_feature_class=CURB_CUT_CopyFeatures)

        # Process: Select: Intersections (Select) (analysis)
        Curb_Cuts_Intersections = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Curb_Cuts_Intersections"
        arcpy.analysis.Select(in_features=CURB_CUT_CopyFeatures, out_feature_class=Curb_Cuts_Intersections, where_clause="SUB_FEATURE_CODE = 222700")

        # Process: Pairwise Buffer: 30ft Intersections (Pairwise Buffer) (analysis)
        Curb_Cuts_Intersection_Buffer = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Scrap.gdb\\Curb_Cuts_Intersection_Buffer"
        arcpy.analysis.PairwiseBuffer(in_features=Curb_Cuts_Intersections, out_feature_class=Curb_Cuts_Intersection_Buffer, buffer_distance_or_field="30 Feet")

        # Process: Copy Features (5) (Copy Features) (management)
        Subway_Lines_2_ = fr"{arcpy.env.scratchGDB}\Subway_Lines"
        arcpy.management.CopyFeatures(in_features=Subway_Lines, out_feature_class=Subway_Lines_2_)

        # Process: Pairwise Buffer (9) (Pairwise Buffer) (analysis)
        Subway_Lines_Buffer = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Subway_Lines_Buffer"
        arcpy.analysis.PairwiseBuffer(in_features=Subway_Lines_2_, out_feature_class=Subway_Lines_Buffer, buffer_distance_or_field="80 Feet")

        # Process: Export Table (2) (Export Table) (conversion)
        Workorders = fr"{arcpy.env.scratchGDB}\Workorders"
        arcpy.conversion.ExportTable(in_table=Workorders_csv, out_table=Workorders, field_mapping="WO \"WO\" true true false 4 Long 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\Excel\\Workorders.csv,WO,-1,-1;XCoordinate \"XCoordinate\" true true false 8 Double 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\Excel\\Workorders.csv,XCoordinate,-1,-1;YCoordinate \"YCoordinate\" true true false 8 Double 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\Excel\\Workorders.csv,YCoordinate,-1,-1")

        # Process: XY Table To Point (2) (XY Table To Point) (management)
        Workorders_XYTableToPoint = fr"{arcpy.env.scratchGDB}\Workorders_XYTableToPoint"
        arcpy.management.XYTableToPoint(in_table=Workorders, out_feature_class=Workorders_XYTableToPoint, x_field="XCoordinate", y_field="YCoordinate", coordinate_system="PROJCS[\"NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet\",GEOGCS[\"GCS_North_American_1983\",DATUM[\"D_North_American_1983\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Lambert_Conformal_Conic\"],PARAMETER[\"False_Easting\",984250.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",-74.0],PARAMETER[\"Standard_Parallel_1\",40.66666666666666],PARAMETER[\"Standard_Parallel_2\",41.03333333333333],PARAMETER[\"Latitude_Of_Origin\",40.16666666666666],UNIT[\"Foot_US\",0.3048006096012192]];-120039300 -96540300 3048.00609601219;-100000 10000;-100000 10000;3.28083333333333E-03;0.001;0.001;IsHighPrecision")

        # Process: Pairwise Buffer: 25 ft per canceled WO (Pairwise Buffer) (analysis)
        WorkOrders_Buffer_3_ = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\WorkOrders_Buffer"
        arcpy.analysis.PairwiseBuffer(in_features=Workorders_XYTableToPoint, out_feature_class=WorkOrders_Buffer_3_, buffer_distance_or_field="25 Feet", dissolve_option="ALL")

        # Process: Export Table (Export Table) (conversion)
        TreenSite = fr"{arcpy.env.scratchGDB}\TreenSite"
        arcpy.conversion.ExportTable(in_table=TreeandSite_csv, out_table=TreenSite, field_mapping="PlantingSpaceID \"PlantingSpaceID\" true true false 4 Long 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\Excel\\TreeandSite.csv,PlantingSpaceID,-1,-1;TreeID \"TreeID\" true true false 4 Long 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\Excel\\TreeandSite.csv,TreeID,-1,-1;XCoordinate \"XCoordinate\" true true false 8 Double 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\Excel\\TreeandSite.csv,XCoordinate,-1,-1;YCoordinate \"YCoordinate\" true true false 8 Double 0 0,First,#,D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\.\\Excel\\TreeandSite.csv,YCoordinate,-1,-1")

        # Process: XY Table To Point (XY Table To Point) (management)
        TreenSite_XYTableToPoint = fr"{arcpy.env.scratchGDB}\TreenSite_XYTableToPoint"
        arcpy.management.XYTableToPoint(in_table=TreenSite, out_feature_class=TreenSite_XYTableToPoint, x_field="XCoordinate", y_field="YCoordinate", coordinate_system="PROJCS[\"NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet\",GEOGCS[\"GCS_North_American_1983\",DATUM[\"D_North_American_1983\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Lambert_Conformal_Conic\"],PARAMETER[\"False_Easting\",984250.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",-74.0],PARAMETER[\"Standard_Parallel_1\",40.66666666666666],PARAMETER[\"Standard_Parallel_2\",41.03333333333333],PARAMETER[\"Latitude_Of_Origin\",40.16666666666666],UNIT[\"Foot_US\",0.3048006096012192]];-120039300 -96540300 3048.00609601219;-100000 10000;-100000 10000;3.28083333333333E-03;0.001;0.001;IsHighPrecision")

        # Process: Pairwise Buffer: 25 ft per Tree (Pairwise Buffer) (analysis)
        TreeAndSite_Buffer_2_ = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\TreeAndSite_Buffer"
        arcpy.analysis.PairwiseBuffer(in_features=TreenSite_XYTableToPoint, out_feature_class=TreeAndSite_Buffer_2_, buffer_distance_or_field="25 Feet", dissolve_option="NONE")

        # Process: Copy Features (7) (Copy Features) (management)
        Grass_Shrub = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Grass_Shrub"
        arcpy.management.CopyFeatures(in_features=Grass_Shrub_ExportFeatures, out_feature_class=Grass_Shrub)

        # Process: Delete Field (Delete Field) (management)
        Grass_Shrub_ExportFeatures_CopyFeatures = arcpy.management.DeleteField(in_table=Grass_Shrub, drop_field=["Id", "gridcode"])[0]

        # Process: Add Field (Add Field) (management)
        Grass_Shrub_ExportFeatures_CopyFeatures_2_ = arcpy.management.AddField(in_table=Grass_Shrub_ExportFeatures_CopyFeatures, field_name="Pit_Type", field_type="TEXT", field_length=10, field_is_required="NON_REQUIRED")[0]

        # Process: Calculate Field (Calculate Field) (management)
        Grass_Shrub_ExportFeatures_CopyFeatures_3_ = arcpy.management.CalculateField(in_table=Grass_Shrub_ExportFeatures_CopyFeatures_2_, field="Pit_Type", expression="\"EP/LP\"")[0]

        # Process: Copy Features (Copy Features) (management)
        HVI_CensusTracts_v2013_CopyFeatures_3_ = fr"{arcpy.env.scratchGDB}\HVI_CensusTracts_v2013_CopyFeatures"
        arcpy.management.CopyFeatures(in_features=FHNR_Datasets_FHNR_HVI_CensusTracts_v2013_2_, out_feature_class=HVI_CensusTracts_v2013_CopyFeatures_3_)

        # Process: Delete Field (2) (Delete Field) (management)
        HVI_CensusTracts_v2013_CopyFeatures = arcpy.management.DeleteField(in_table=HVI_CensusTracts_v2013_CopyFeatures_3_, drop_field=["BoroName", "BoroCT2010", "PUMA", "NTAName", "NTACode", "Shape_Leng", "BoroCD", "GlobalID", "Borough", "ONENYC_HVI"])[0]

        # Process: Alter Field (Alter Field) (management)
        HVI_CensusTracts_v2013_CopyFeatures_2_ = arcpy.management.AlterField(in_table=HVI_CensusTracts_v2013_CopyFeatures, field="QUINTILES", new_field_name="HVI_CT_2013", clear_field_alias="CLEAR_ALIAS")[0]

        # Process: Union (Union) (analysis)
        Political_Boundary_Final = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Political_Boundary_Final"
        arcpy.analysis.Union(in_features=[[Political_Boundary, ""], [HVI_CensusTracts_v2013_CopyFeatures_2_, ""], [NYCDOHMH_HVI_CensusTracts_2018_Clip, ""], [NYCDOHMH_HVI_CensusTracts_2023, ""], [NYCDOHMH_HVI_NeighborhoodTabulationAreas_2018, ""], [NYCDOHMH_HVI_NeighborhoodTabulationAreas_2023, ""], [NYCDCP_Borough_Boundaries_Water_Included, ""], [NYCDCP_Borough_Boundaries, ""]], out_feature_class=Political_Boundary_Final)

        # Process: Delete Field (3) (Delete Field) (management)
        Political_Boundary_Final_2_ = arcpy.management.DeleteField(in_table=Political_Boundary_Final, drop_field=["FID_Political_Boundary", "FID_NYCDOHMH_HVI_CensusTracts_2018_Clip", "FID_NYCDOHMH_HVI_CensusTracts_2023", "FID_NYCDOHMH_HVI_NeighborhoodTabulationAreas_2018", "FID_NYCDOHMH_HVI_NeighborhoodTabulationAreas_2023", "FID_NYCDCP_Borough_Boundaries_Water_Included", "FID_NYCDCP_Borough_Boundaries", "FID_HVI_CensusTracts_v2013_CopyFeatures"])[0]

        # Process: Pairwise Buffer: 20ft Intersections (Pairwise Buffer) (analysis)
        Curb_Cuts_Intersection_20ft = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Curb_Cuts_Intersection_20ft"
        arcpy.analysis.PairwiseBuffer(in_features=Curb_Cuts_Intersections, out_feature_class=Curb_Cuts_Intersection_20ft, buffer_distance_or_field="20 Feet")

        # Process: Select: Pedestrian Streets (Select) (analysis)
        Street_Centerline_Select = fr"{arcpy.env.scratchGDB}\Street_Centerline_Select"
        arcpy.analysis.Select(in_features=Street_Centerline, out_feature_class=Street_Centerline_Select, where_clause="L_LOW_HN <> ''")

        # Process: Simplify: Pedestrian Streets (Simplify Line) (cartography)
        Street_Centerli_SimplifyLine = fr"{arcpy.env.scratchGDB}\Street_Centerli_SimplifyLine"
        with arcpy.EnvManager(transferGDBAttributeProperties=False):
            Street_Centerli_SimplifyLine_Pnt = arcpy.cartography.SimplifyLine(in_features=Street_Centerline_Select, out_feature_class=Street_Centerli_SimplifyLine, algorithm="POINT_REMOVE", tolerance="1 Feet")[0]

        # Process: Feature Vertices To Points: Start/End (Feature Vertices To Points) (management)
        Street_Vertices_Points = fr"{arcpy.env.scratchGDB}\Street_Vertices_Points"
        arcpy.management.FeatureVerticesToPoints(in_features=Street_Centerli_SimplifyLine, out_feature_class=Street_Vertices_Points, point_location="BOTH_ENDS")

        # Process: Pairwise Buffer: 40ft End Points (Pairwise Buffer) (analysis)
        Street_Centerl_PairwiseBuffe = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Street_Vertice_Buffer"
        arcpy.analysis.PairwiseBuffer(in_features=Street_Vertices_Points, out_feature_class=Street_Centerl_PairwiseBuffe, buffer_distance_or_field="40 Feet")

        # Process: Near: Hydrants to Sidewalks (Near) (analysis)
        Hydrants_1 = arcpy.analysis.Near(in_features=DEP_Hydrants, near_features=[Sidewalk_Pluto], search_radius="10 DecimalDegrees", location="LOCATION", distance_unit="Feet")[0]

        # Process: MoveStreetSigns (MoveStreetSigns) (StreetTreePlantingAnalysisPython)
        Hydrants_2 = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Street_Tree_Planting_Analysis.gdb\\Hydrants_Corrected"
        arcpy.StreetTreePlantingAnalysisPython.MoveStreetSigns(input_fc=Hydrants_1, output_fc=Hydrants_2)

        # Process: Pairwise Buffer: 3ft (Pairwise Buffer) (analysis)
        Hydrants_Final = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\DEP_Hydrants_PairwiseBuffer"
        arcpy.analysis.PairwiseBuffer(in_features=Hydrants_2, out_feature_class=Hydrants_Final, buffer_distance_or_field="3 Feet")

        # Process: Select: Curb Cut Driveway (Select) (analysis)
        Curb_Cuts_Driveways = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Curb_Cuts_Driveways"
        arcpy.analysis.Select(in_features=CURB_CUT_CopyFeatures, out_feature_class=Curb_Cuts_Driveways, where_clause="SUB_FEATURE_CODE = 222600")

        # Process: Python Script: Curb Cut Buffer Calculation (Curb Cut Buffer Calculation) (StreetTreePlantingAnalysisPython)
        Curb_Cuts_Driveways_Buffer = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Curb_Cuts_Driveways_Buffer"
        arcpy.StreetTreePlantingAnalysisPython.CurbCuts(input_feature_class=Curb_Cuts_Driveways, output_feature_class=Curb_Cuts_Driveways_Buffer, extension_distance=7, buffer_width=15)

        # Process: Union (2) (Union) (analysis)
        Vaults = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Vaults"
        arcpy.analysis.Union(in_features=[[BK_Vaults_Buffer_2_, ""], [DOT_Vault_Buffer_2_, ""]], out_feature_class=Vaults)

        # Process: Delete Field (4) (Delete Field) (management)
        Vaults_5_ = arcpy.management.DeleteField(in_table=Vaults, drop_field=["FID_BK_Vaults_Buffer", "Shape_Leng", "OID_", "Rec_Num", "Boro", "BLCK", "Lot", "Dimensions", "Num_Vaults", "Location", "Data", "BUFF_DIST", "ORIG_FID", "FID_DOT_Vault_Buffer", "BL_Junk_CD", "BL_Junk_CB", "BL_Junk_Zi", "BL_Junk_Ad", "BL_Junk__9", "Junk_LOCAT", "BUFF_DIST_1", "ORIG_FID_1"])[0]

        # Process: Add Field (2) (Add Field) (management)
        Vaults_3_ = arcpy.management.AddField(in_table=Vaults_5_, field_name="Vaults", field_type="LONG")[0]

        # Process: Calculate Field (2) (Calculate Field) (management)
        Vaults_4_ = arcpy.management.CalculateField(in_table=Vaults_3_, field="Vaults", expression="1")[0]

        # Process: Union (3) (Union) (analysis)
        Output_Feature_Class = ""
        arcpy.analysis.Union(in_features=[], out_feature_class=Output_Feature_Class)

        # Process: Pairwise Buffer (Pairwise Buffer) (analysis)
        Curb_Cuts_Intersection_10ft_2_ = "D:\\ArcGIS\\Projects\\Street_Tree_Planting_Analysis\\Refresh.gdb\\Curb_Cuts_Intersection_10ft"
        arcpy.analysis.PairwiseBuffer(in_features=Curb_Cuts_Intersections, out_feature_class=Curb_Cuts_Intersection_10ft_2_, buffer_distance_or_field="10 Feet")

if __name__ == '__main__':
    # Global Environment settings
    with arcpy.EnvManager(autoCommit=1000, baUseDetailedAggregation=False, cellAlignment="DEFAULT", 
                          cellSize="MAXOF", cellSizeProjectionMethod="CONVERT_UNITS", coincidentPoints="MEAN", 
                          compression="LZ77", maintainAttachments=True, maintainSpatialIndex=False, 
                          matchMultidimensionalVariable=True, nodata="NONE", outputMFlag="Same As Input", 
                          outputZFlag="Same As Input", preserveGlobalIds=False, pyramid="PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP NO_SIPS", 
                          qualifiedFieldNames=True, randomGenerator="0 ACM599", rasterStatistics="STATISTICS 1 1", 
                          resamplingMethod="NEAREST", terrainMemoryUsage=False, tileSize="128 128", 
                          tinSaveVersion="CURRENT", transferDomains=False, transferGDBAttributeProperties=False, 
                          unionDimension=False):
        Refresh()
