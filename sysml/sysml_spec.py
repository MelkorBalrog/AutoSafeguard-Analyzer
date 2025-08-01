# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import re
import os


def load_sysml_properties():
    path = os.path.join(os.path.dirname(__file__), 'SysML.xmi')
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    start = text.find('<xmi:XMI')
    if start == -1:
        return {}
    text = text[start:]
    class_pattern = re.compile(r'<packagedElement[^>]*xmi:type="uml:Class"[^>]*name="([^"]+)"')
    attr_pattern = re.compile(r'<ownedAttribute[^>]*name="([^"]+)"')
    props = {}
    for m in class_pattern.finditer(text):
        name = m.group(1)
        end = text.find('</packagedElement>', m.end())
        if end == -1:
            continue
        block = text[m.end():end]
        attrs = attr_pattern.findall(block)
        props[name] = attrs
    return props

SYSML_PROPERTIES = load_sysml_properties()
if 'BlockUsage' not in SYSML_PROPERTIES:
    SYSML_PROPERTIES['BlockUsage'] = [
        'partProperties',
        'ports',
        'operations',
        'behaviors',
    ]
if 'PortUsage' not in SYSML_PROPERTIES:
    SYSML_PROPERTIES['PortUsage'] = []
for p in ('direction', 'flow'):
    if p not in SYSML_PROPERTIES['PortUsage']:
        SYSML_PROPERTIES['PortUsage'].append(p)
for p in ('labelX', 'labelY'):
    if p not in SYSML_PROPERTIES['PortUsage']:
        SYSML_PROPERTIES['PortUsage'].append(p)

if 'BlockBoundaryUsage' not in SYSML_PROPERTIES:
    SYSML_PROPERTIES['BlockBoundaryUsage'] = list(SYSML_PROPERTIES.get('BlockUsage', []))

# ----------------------------------------------------------------------
# Additional properties for reliability annotations
# ----------------------------------------------------------------------
# Blocks can reference reliability analyses while parts map to components.
# Include dedicated attributes to reference BOM items and store FIT,
# qualification and failure mode details so they can be displayed in diagrams.

SYSML_PROPERTIES.setdefault('BlockUsage', [])
SYSML_PROPERTIES.setdefault('PartUsage', [])

# Remove the derived SysML property 'partDefinition' from PartUsage entries.
if 'partDefinition' in SYSML_PROPERTIES['PartUsage']:
    SYSML_PROPERTIES['PartUsage'].remove('partDefinition')

for prop in ('analysis', 'fit', 'qualification', 'failureModes'):
    if prop not in SYSML_PROPERTIES['BlockUsage']:
        SYSML_PROPERTIES['BlockUsage'].append(prop)

# Remove the derived SysML property 'actionDefinition' from ActionUsage entries.
if 'actionDefinition' in SYSML_PROPERTIES.get('ActionUsage', []):
    SYSML_PROPERTIES['ActionUsage'].remove('actionDefinition')

for prop in (
    'component',
    'failureModes',
    'asil',
    'force_ibd',
    'ports',
    'operations',
    'partProperties',
    'behaviors',
):
    if prop not in SYSML_PROPERTIES['PartUsage']:
        SYSML_PROPERTIES['PartUsage'].append(prop)

# Keep BlockBoundaryUsage in sync with BlockUsage properties, including
# reliability annotations.
SYSML_PROPERTIES['BlockBoundaryUsage'] = list(SYSML_PROPERTIES['BlockUsage'])
