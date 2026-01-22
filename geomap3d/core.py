import json
import os
import webbrowser

class Map:
    def __init__(self, time_steps=None,interaction="click"):
        self.shapes = [] #** Stores shapes *
        self.surfaces = [] #** Stores surfaces *
        self.interaction = interaction

        self.bounds = {
            'min_lat': 90,
            'max_lat': -90,
            'min_lon': 180,
            'max_lon': -180
        } #**Auto-centering, auto-scaling, zoom calculation* -_-

        self.time_steps = list(time_steps) if time_steps else [] #Initial timeline values.
        # **** if m = GeoMap3D(time_steps=None) then self.time_steps becomes []
        # **** if tuple, m = GeoMap3D(time_steps=("9am", "10am")) then self.time_steps becomes ["9am", "10am"]
        #**** if time_steps=["00:00", "01:00", "02:00"] then list(["00:00", "01:00", "02:00"])

    def _update_bounds(self, points):
        for lon, lat in points:
            self.bounds['min_lat'] = min(self.bounds['min_lat'], lat)
            self.bounds['max_lat'] = max(self.bounds['max_lat'], lat)
            self.bounds['min_lon'] = min(self.bounds['min_lon'], lon)
            self.bounds['max_lon'] = max(self.bounds['max_lon'], lon)

    # PUBLIC API (what users call)
    def add_bar(self, polygon, height=10, color="#ffffff", time=0,info=None):
        self._update_bounds(polygon)

        if time not in self.time_steps:
            self.time_steps.append(time)

        self.shapes.append({
            "raw_coords": polygon,
            "height": height,
            "color": color,
            "time": time,
            "info": info or {}
        })

    def add_surface(self, points, color="#00ff88", opacity=0.6, time=0):
        self._update_bounds([(p[0], p[1]) for p in points])

        if time not in self.time_steps:
            self.time_steps.append(time)

        self.surfaces.append({
            "points": points,
            "color": color,
            "opacity": opacity,
            "time": time
        })

    # INTERNAL
    def _project(self):
        center_lat = (self.bounds['min_lat'] + self.bounds['max_lat']) / 2
        center_lon = (self.bounds['min_lon'] + self.bounds['max_lon']) / 2

        span = max(
            self.bounds['max_lat'] - self.bounds['min_lat'],
            self.bounds['max_lon'] - self.bounds['min_lon'],
            0.00001
        )

        zoom = 1000 / span

        for s in self.shapes:
            s['coords'] = [
                [(lon - center_lon) * zoom, (lat - center_lat) * zoom]
                for lon, lat in s['raw_coords']
            ]

        for surf in self.surfaces:
            surf['projected'] = [
                [(lon - center_lon) * zoom, (lat - center_lat) * zoom, z * 2]
                for lon, lat, z in surf['points']
            ]

    def show(self, filename="geomap3d.html"):
        self._project()

        base_dir = os.path.dirname(__file__)
        template_path = os.path.join(base_dir, 'templates', 'viewer.html')

        with open(template_path, 'r', encoding="utf-8") as f:
            html = f.read()

        # steps = sorted(self.time_steps)
        steps = sorted(set(self.time_steps))


        config = {
            "shapes": self.shapes,
            "surfaces": self.surfaces,
            "timeSteps": steps,
            "maxTimeIndex": len(steps) - 1,
            "interaction": self.interaction,
        }

        html = html.replace("{{ MAP_DATA }}", json.dumps(config))

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open("file://" + os.path.abspath(filename))
