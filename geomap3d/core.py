import json
import os
import webbrowser

class Map:
    def __init__(self): 
        self.shapes = []
        self.surfaces = [] 
        self.bounds = {'min_lat': 90, 'max_lat': -90, 'min_lon': 180, 'max_lon': -180}
        self.time_steps = set()

    def _update_bounds(self, points):
        for lon, lat in points:
            self.bounds['min_lat'] = min(self.bounds['min_lat'], lat)
            self.bounds['max_lat'] = max(self.bounds['max_lat'], lat)
            self.bounds['min_lon'] = min(self.bounds['min_lon'], lon)
            self.bounds['max_lon'] = max(self.bounds['max_lon'], lon)

    def add_data(self, coords, height=10, color="#ffffff", time=0):
        self._update_bounds(coords)
        self.time_steps.add(time)
        self.shapes.append({"raw_coords": coords, "height": height, "color": color, "time": time})

    def add_surface(self, points, color="#00ff88", opacity=0.6, time=0):
        self._update_bounds([(p[0], p[1]) for p in points])
        self.time_steps.add(time)
        self.surfaces.append({"points": points, "color": color, "opacity": opacity, "time": time})

    def _project(self):
        center = [(self.bounds['min_lat'] + self.bounds['max_lat'])/2, (self.bounds['min_lon'] + self.bounds['max_lon'])/2]
        zoom = 1000 / max(0.00001, self.bounds['max_lat'] - self.bounds['min_lat'])
        for s in self.shapes:
            s['coords'] = [[(p[0]-center[1])*zoom, (p[1]-center[0])*zoom] for p in s['raw_coords']]
        for surf in self.surfaces:
            # Scale height by 2 so mesh is thick enough to see
            surf['projected'] = [[(p[0]-center[1])*zoom, (p[1]-center[0])*zoom, p[2]*2] for p in surf['points']]

    def show(self, filename="researcher_map.html"):
        self._project()
        base_dir = os.path.dirname(__file__)
        template_path = os.path.join(base_dir, 'templates', 'viewer.html')
        if not os.path.exists(template_path): template_path = 'viewer.html'
        with open(template_path, 'r') as f: html = f.read()
        steps = sorted(list(self.time_steps))
        config = {"shapes": self.shapes, "surfaces": self.surfaces, "timeSteps": steps, "maxTimeIndex": len(steps)-1}
        html = html.replace("{{ MAP_DATA }}", json.dumps(config))
        with open(filename, "w") as f: f.write(html)
        webbrowser.open("file://" + os.path.realpath(filename))