CURRENT_DATABASE_VERSION = 2


def _migrate_v1(data: dict) -> dict:

    world_asset_id_to_name = {
        world["asset_id"]: world["name"]
        for world in data["worlds"]
    }
    area_asset_id_to_name = {
        world["name"]: {
            area["asset_id"]: area["name"]
            for area in world["areas"]
        }
        for world in data["worlds"]
    }

    start_loc = data["starting_location"]
    data["starting_location"] = {
        "world_name": world_asset_id_to_name[start_loc["world_asset_id"]],
        "area_name": area_asset_id_to_name[world_asset_id_to_name[start_loc["world_asset_id"]]][
            start_loc["area_asset_id"]
        ],
    }

    for world in data["worlds"]:
        world_name = world["name"]
        new_areas = {}

        if world.get("extra") is None:
            world["extra"] = {}

        world["extra"]["asset_id"] = world.pop("asset_id")
        if (dark_name := world.pop("dark_name")) is not None:
            world["extra"]["dark_name"] = dark_name

        for area in world["areas"]:
            area_name = area.pop("name")
            if area_name in new_areas:
                raise ValueError("Name conflict in {}: {}".format(world["name"], area_name))

            if area.get("extra") is None:
                area["extra"] = {}

            area["extra"]["asset_id"] = area.pop("asset_id")
            if dark_name is not None:
                area["extra"]["in_dark_aether"] = area.pop("in_dark_aether")

            new_nodes = {}
            for node in area["nodes"]:
                node_name = node.pop("name")

                if node_name in new_nodes:
                    raise ValueError("Name conflict in {} - {}: {}".format(world["name"], area_name, node_name))

                if node.get("extra") is None:
                    node["extra"] = {}

                if node["node_type"] == "dock":
                    node["connected_area_name"] = area_asset_id_to_name[world_name][node.pop("connected_area_asset_id")]

                elif node["node_type"] == "teleporter":
                    dest_world_name = world_asset_id_to_name[node.pop("destination_world_asset_id")]
                    dest_area_name = area_asset_id_to_name[dest_world_name][node.pop("destination_area_asset_id")]
                    node["destination"] = {"world_name": dest_world_name, "area_name": dest_area_name}
                    node["extra"]["scan_asset_id"] = node.pop("scan_asset_id")
                    node["extra"]["teleporter_instance_id"] = node.pop("teleporter_instance_id")

                new_nodes[node_name] = node

            area["nodes"] = new_nodes
            new_areas[area_name] = area

        world["areas"] = new_areas

    return data


_MIGRATIONS = {
    1: _migrate_v1,
}


def migrate_to_current(data: dict) -> dict:
    schema_version = data.get("schema_version", 1)

    while schema_version < CURRENT_DATABASE_VERSION:
        data = _MIGRATIONS[schema_version](data)
        schema_version += 1

    return data
