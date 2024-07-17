import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import cartopy.crs as ccrs
from cartopy.io.img_tiles import MapboxTiles
import geopandas as gpd
import os
from dotenv import load_dotenv
import random

"""
This module provides functionality for mapping parcels and buildings using various data sources and visualization methods.

The main class, ParcelBuildingMapper, handles loading, processing, and visualizing geospatial data for parcels and buildings.
"""

class ParcelBuildingMapper:
    """
    A class for mapping parcels and buildings using various data sources and visualization methods.

    This class provides methods for loading geospatial data, processing it, and creating visualizations
    of parcels and buildings using different mapping techniques.

    Attributes:
        parcels_path (str): Path to the parcels shapefile.
        buildings_path (str): Path to the buildings shapefile.
        epsg (int): EPSG code for the coordinate reference system (default is 3857).
        df_parcels (GeoDataFrame): GeoDataFrame containing parcel data.
        df_buildings (GeoDataFrame): GeoDataFrame containing building data.
        df_parcels_buildings (GeoDataFrame): GeoDataFrame containing joined parcel and building data.

    """
     
    def __init__(self, parcels_path, buildings_path, epsg=3857):
        """
        Initialize the ParcelBuildingMapper with paths to parcel and building data.

        Args:
            parcels_path (str): Path to the parcels shapefile.
            buildings_path (str): Path to the buildings shapefile.
            epsg (int, optional): EPSG code for the coordinate reference system. Defaults to 3857.
        """

        load_dotenv()
        self.parcels_path = parcels_path
        self.buildings_path = buildings_path
        self.epsg = epsg
        self.df_parcels = None
        self.df_buildings = None
        self.df_parcels_buildings = None
        self.load_data()

    def load_data(self):
        """
        Load parcel and building data from shapefiles and prepare it for mapping.

        This method reads the shapefile data, transforms it to the specified coordinate system,
        assigns random colors to parcels, and joins the parcel and building data.
        """

        self.df_parcels = gpd.read_file(self.parcels_path)
        self.df_buildings = gpd.read_file(self.buildings_path)
        
        self.df_parcels = self.df_parcels.to_crs(epsg=self.epsg)
        self.df_buildings = self.df_buildings.to_crs(epsg=self.epsg)
        
        self.df_parcels['color'] = [self.random_hex_color() for _ in range(len(self.df_parcels))]
        self.df_parcels_buildings = self.join_parcels_buildings(self.df_parcels, self.df_buildings)

    def random_hex_color(self, use_seed=False):
        """
        Generate a random hex color code.

        Args:
            use_seed (bool, optional): Whether to use a seed for random number generation. Defaults to False.

        Returns:
            str: A randomly generated hex color code.
        """

        if use_seed:
            random.seed(use_seed)
            r = random.randint(0, 255)
            random.seed(use_seed+1000)
            g = random.randint(0, 255)
            random.seed(use_seed+2000)
            b = random.randint(0, 255)
        else:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def join_parcels_buildings(self, parcels, buildings):
        """
        Join parcel and building data based on spatial relationship.

        Args:
            parcels (GeoDataFrame): GeoDataFrame containing parcel data.
            buildings (GeoDataFrame): GeoDataFrame containing building data.

        Returns:
            GeoDataFrame: A GeoDataFrame containing joined parcel and building data.
        """

        return buildings.sjoin(parcels, how="inner")

    def add_geometries(self, ax, df_parcels, crs_epsg, random_color=False):
        """
        Add geometries to the given axes object.

        Args:
            ax (GeoAxesSubplot): The axes object to add geometries to.
            df_parcels (GeoDataFrame): GeoDataFrame containing parcel data.
            crs_epsg (CRS): Coordinate reference system for the geometries.
            random_color (bool, optional): Whether to use random colors. Defaults to False.
        """

        for row in df_parcels.itertuples():
            geometry = row.geometry
            if random_color:
                color = self.random_hex_color(int(row.bin))
            else:
                color = row.color
            ax.add_geometries(geometry, crs=crs_epsg, facecolor=color)

    def map_maker_mapbox_satellite(self, df_parcels, df_buildings, bounds, index, scale=10, feature_type='both', random_color=False, output_folder=''):
        """
        Create a map using Mapbox satellite imagery as a base layer.

        Args:
            df_parcels (GeoDataFrame): GeoDataFrame containing parcel data.
            df_buildings (GeoDataFrame): GeoDataFrame containing building data.
            bounds (tuple): Bounding box for the map (minx, miny, maxx, maxy).
            index (int): Index for the output filename.
            scale (int, optional): Zoom level for the satellite imagery. Defaults to 10.
            feature_type (str, optional): Type of features to display ('parcels', 'buildings', or 'both'). Defaults to 'both'.
            random_color (bool, optional): Whether to use random colors. Defaults to False.
            output_folder (str, optional): Folder to save the output image. Defaults to ''.
        """

        access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
        tiler = MapboxTiles(access_token, 'satellite-v9')
        crs_epsg = ccrs.epsg(str(self.epsg))
        mercator = tiler.crs

        fig = plt.figure(figsize=(7, 7), dpi=96)
        ax = fig.add_subplot(1, 1, 1, projection=mercator)

        dist1 = bounds[2] - bounds[0]
        dist2 = bounds[3] - bounds[1]
        max_dist = max(dist1, dist2) / 2
        centroid_x = (bounds[2] + bounds[0]) / 2
        centroid_y = (bounds[3] + bounds[1]) / 2

        ax.set_extent([centroid_x-max_dist, centroid_x+max_dist, centroid_y-max_dist, centroid_y+max_dist], crs=crs_epsg)

        if feature_type in ['parcels', 'both']:
            self.add_geometries(ax, df_parcels, crs_epsg, random_color)
        if feature_type in ['buildings', 'both']:
            self.add_geometries(ax, df_buildings, crs_epsg, random_color)

        ax.add_image(tiler, scale)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        plt.savefig(os.path.join(output_folder, f'{feature_type}_{index}.jpg'), bbox_inches='tight', pad_inches=0, dpi=96)
        plt.close(fig)

    def map_maker_simple(self, df_parcels, df_buildings, bounds, index, feature_type='both', random_color=False, output_folder=''):
        """
        Create a simple map without satellite imagery.

        Args:
            df_parcels (GeoDataFrame): GeoDataFrame containing parcel data.
            df_buildings (GeoDataFrame): GeoDataFrame containing building data.
            bounds (tuple): Bounding box for the map (minx, miny, maxx, maxy).
            index (int): Index for the output filename.
            feature_type (str, optional): Type of features to display ('parcels', 'buildings', or 'both'). Defaults to 'both'.
            random_color (bool, optional): Whether to use random colors. Defaults to False.
            output_folder (str, optional): Folder to save the output image. Defaults to ''.
        """

        fig, ax = plt.subplots(figsize=(7, 7))
        
        if feature_type in ['parcels', 'both']:
            df_parcels.plot(ax=ax, facecolor=df_parcels['color'], edgecolor='black', linewidth=0.5)
        if feature_type in ['buildings', 'both']:
            df_buildings.plot(ax=ax, facecolor='red', edgecolor='black', linewidth=0.5)
        
        ax.set_xlim(bounds[0], bounds[2])
        ax.set_ylim(bounds[1], bounds[3])
        ax.axis('off')
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        plt.savefig(os.path.join(output_folder, f'{feature_type}_{index}.jpg'), bbox_inches='tight', pad_inches=0, dpi=96)
        plt.close(fig)

    def subset(self, df, df_buildings, index, distance=75):
        """
        Create a subset of the data based on a buffer around a selected feature.

        Args:
            df (GeoDataFrame): GeoDataFrame containing parcel data.
            df_buildings (GeoDataFrame): GeoDataFrame containing building data.
            index (int): Index of the feature to create a subset around.
            distance (float, optional): Buffer distance in meters. Defaults to 75.

        Returns:
            tuple: A tuple containing:
                - GeoDataFrame: Subset of parcel data.
                - GeoDataFrame: Subset of building data.
                - tuple: Bounding box of the subset area.
        """

        selected_feature = df.loc[index]
        geometry_buffer = selected_feature.geometry.buffer(distance)
        geometry_bounds = selected_feature.geometry.buffer(distance-70)
        return df[df.within(geometry_buffer)], df_buildings[df_buildings.within(geometry_buffer)], geometry_bounds.bounds

    def generate_maps(self, parcels_output_path, buildings_output_path, start_index=0, end_index=10, distance=75, map_type='mapbox_satellite'):
        """
        Generate maps for a range of indices using the specified map type.

        Args:
            parcels_output_path (str): Output folder for parcel maps.
            buildings_output_path (str): Output folder for building maps.
            start_index (int, optional): Starting index for map generation. Defaults to 0.
            end_index (int, optional): Ending index for map generation. Defaults to 10.
            distance (float, optional): Buffer distance in meters for subsetting. Defaults to 75.
            map_type (str, optional): Type of map to generate ('mapbox_satellite' or 'simple'). Defaults to 'mapbox_satellite'.
        """
        
        for i in range(start_index, end_index):
            subset_features = self.subset(self.df_parcels, self.df_parcels_buildings, i, distance)
            
            if map_type == 'mapbox_satellite':
                self.map_maker_mapbox_satellite(subset_features[0], subset_features[1], subset_features[2], i, 18, 'buildings', output_folder=buildings_output_path)
                self.map_maker_mapbox_satellite(subset_features[0], subset_features[1], subset_features[2], i, 18, 'parcels', output_folder=parcels_output_path)
            elif map_type == 'simple':
                self.map_maker_simple(subset_features[0], subset_features[1], subset_features[2], i, 'buildings', output_folder=buildings_output_path)
                self.map_maker_simple(subset_features[0], subset_features[1], subset_features[2], i, 'parcels', output_folder=parcels_output_path)
            else:
                raise ValueError(f"Unsupported map type: {map_type}")
        plt.close('all')

if __name__ == "__main__":
    parcels_path = "C:/Million Neighborhoods/Spatial Data/ny-manhattan-parcels/NYC_2021_Tax_Parcels_SHP_2203/NewYork_2021_Tax_Parcels_SHP_2203.shp"
    buildings_path = "C:/Million Neighborhoods/Spatial Data/ny-manhattan-buildings/geo_export_a80ea1a2-e8e0-4ffd-862c-1199433ac303.shp"
    mapper = ParcelBuildingMapper(parcels_path, buildings_path)
    
    parcels_output_path = "C:/Million Neighborhoods/Spatial Data/result/parcels/"
    buildings_output_path = "C:/Million Neighborhoods/Spatial Data/result/buildings/"
    
    # Generate maps using Mapbox satellite imagery
    mapper.generate_maps(parcels_output_path, buildings_output_path, start_index=0, end_index=5, distance=200, map_type='mapbox_satellite')
    
    # Generate simple maps without satellite imagery
    mapper.generate_maps(parcels_output_path, buildings_output_path, start_index=5, end_index=10, distance=200, map_type='simple')
    
