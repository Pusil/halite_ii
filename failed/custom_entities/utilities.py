import hlt
import math
from . import constants
from collections import OrderedDict
import logging


def clean_enemy(entity, enemy):
    distance = constants.IDEAL_DISTANCE - calculate_distance_between(entity, enemy)
    angle = calculate_angle_between(entity, enemy)
    if distance > 0:
        angle = (angle + 180) % 360
    else:
        distance = abs(distance)
    temp_enemy_dx = math.cos(math.radians(angle)) * distance
    temp_enemy_dy = math.sin(math.radians(angle)) * distance
    new_target = hlt.entity.Position(entity.x + temp_enemy_dx, entity.y + temp_enemy_dy)
    return new_target


def navigate(ship, target, game_map, speed, max_corrections=90, angular_step=1,
             direction=1, current_angle=0, distance=0, angle=0, temp_angle=0, dispatch=None):
    if max_corrections <= 0:
        return None
    if not distance:
        distance = calculate_distance_between(ship, target)
    if not angle:
        angle = calculate_angle_between(ship, target)
        temp_angle = angle

    if obstacles_between(game_map, ship, target, dispatch):
        if direction > 0:
            current_angle += angular_step
            temp_angle = (angle + current_angle) % 360
        else:
            temp_angle = (angle - current_angle + 360) % 360
        direction *= -1

        new_target_dx = math.cos(math.radians(temp_angle)) * distance
        new_target_dy = math.sin(math.radians(temp_angle)) * distance
        new_target = hlt.entity.Position(ship.x + new_target_dx, ship.y + new_target_dy)
        return navigate(ship, new_target, game_map, speed, max_corrections - 1, angular_step,
                        current_angle=current_angle, direction=direction, distance=distance, angle=angle,
                        temp_angle=temp_angle, dispatch=dispatch)
    speed = speed if (distance >= speed) else distance
    angle = temp_angle
    dispatch.next_turn_ships.append(hlt.entity.Ship(game_map.get_me().id, 0,
                                                    math.cos(math.radians(angle)) * speed + ship.x,
                                                    math.sin(math.radians(angle)) * speed + ship.y, 1, 0, 0,
                                                    hlt.entity.Ship.DockingStatus.UNDOCKED, 0, 0, 0))
    return thrust(ship, speed, angle)


def obstacles_between(game_map, ship, target, dispatch=None):
    entities = game_map.all_planets() + _all_ships(game_map)
    if dispatch:
        entities += dispatch.next_turn_ships
    for foreign_entity in entities:
        if foreign_entity == ship or foreign_entity == target:
            continue
        if intersect_segment_circle(ship, target, foreign_entity, fudge=ship.radius + 0.1):
            return True
    return False


def obstacles_between_theta_star(game_map, ship, target, ship_to_ignore, dispatch):
    entities = game_map.all_planets() + almost_all_ships(game_map, ship_to_ignore, dispatch)
    for foreign_entity in entities:
        if foreign_entity == ship or foreign_entity == target:
            continue
        if intersect_segment_circle(ship, target, foreign_entity, fudge=0.6):
            return True
    return False


def thrust(ship, magnitude, angle):
    return "t {} {} {}".format(ship.id, int(magnitude), round(angle))


def calculate_angle_between(ship, target):
    return math.degrees(math.atan2(target.y - ship.y, target.x - ship.x)) % 360


def get_nearest_enemy(entity, game_map):
    entities_by_distance = get_nearby_sorted(entity, game_map)
    for distance in entities_by_distance:
        if isinstance(entities_by_distance[distance][0], hlt.entity.Ship):
            if entities_by_distance[distance][0].owner.id != game_map.get_me().id:
                return entities_by_distance[distance][0]
    return None


def get_nearest_friendly(entity, game_map):
    entities_by_distance = get_nearby_sorted(entity, game_map)
    for distance in entities_by_distance:
        if isinstance(entities_by_distance[distance][0], hlt.entity.Ship):
            if entities_by_distance[distance][0].owner.id == game_map.get_me().id:
                return entities_by_distance[distance][0]
    return None


def get_nearest_ship_and_planet(entity, game_map):
    entities_by_distance = get_nearby_sorted(entity, game_map)
    ship = None
    planet = None
    for distance in entities_by_distance:
        if isinstance(entities_by_distance[distance][0], hlt.entity.Ship):
            if entities_by_distance[distance][0].owner != game_map.get_me():
                ship = entities_by_distance[distance][0]
                break
    for distance in entities_by_distance:
        if isinstance(entities_by_distance[distance][0], hlt.entity.Planet):
            planet = entities_by_distance[distance][0]
            break
    return ship, planet


def get_nearby_sorted_docked(entity, game_map):
    entities_by_distance = nearby_entities_by_distance_docked(entity, game_map)
    entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
    return entities_by_distance


def nearby_entities_by_distance_docked(ship, game_map):
    result = {}
    for foreign_entity in game_map.get_me().all_ships():
        if ship == foreign_entity:
            continue
        result.setdefault(calculate_distance_between_docked(ship, foreign_entity), []).append(foreign_entity)
    return result


def calculate_distance_between_docked(ship, foreign_entity):
    result = math.sqrt((foreign_entity.x - ship.x) ** 2 + (foreign_entity.y - ship.y) ** 2)

    if isinstance(foreign_entity, hlt.entity.Ship):
        if foreign_entity.docking_status != foreign_entity.DockingStatus.UNDOCKED:
            result += constants.DOCKED_WEIGHT
    return result


def get_nearby_sorted(entity, game_map):
    entities_by_distance = nearby_entities_by_distance(entity, game_map)
    entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
    return entities_by_distance


def nearby_entities_by_distance(ship, game_map):
    result = {}
    for foreign_entity in _all_ships(game_map) + game_map.all_planets():
        if ship == foreign_entity:
            continue
        result.setdefault(calculate_distance_between(ship, foreign_entity), []).append(foreign_entity)
    return result


def calculate_distance_between(ship, foreign_entity):
    result = math.sqrt((foreign_entity.x - ship.x) ** 2 + (foreign_entity.y - ship.y) ** 2)

    return result


def get_nearby_sorted_planet(entity, game_map):
    entities_by_distance = nearby_entities_by_distance_planet(entity, game_map)
    entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
    return entities_by_distance


def nearby_entities_by_distance_planet(ship, game_map):
    result = {}
    for foreign_entity in _all_ships(game_map) + game_map.all_planets():
        if ship == foreign_entity:
            continue
        result.setdefault(calculate_distance_between_planet(ship, foreign_entity), []).append(foreign_entity)
    return result


def calculate_distance_between_planet(ship, foreign_entity):
    result = math.sqrt((foreign_entity.x - ship.x) ** 2 + (foreign_entity.y - ship.y) ** 2) ** 1.3

    return result


def get_nearby_sorted_squadron(entity, squadrons):
    entities_by_distance = nearby_entities_by_distance_squadron(entity, squadrons)
    entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
    return entities_by_distance


def nearby_entities_by_distance_squadron(ship, squadrons):
    result = {}
    for foreign_entity in squadrons:
        if ship == foreign_entity:
            continue
        result.setdefault(calculate_distance_between(ship, foreign_entity), []).append(foreign_entity)
    return result


def intersect_segment_circle(start, end, circle, *, fudge=0.5):
    """
    Test whether a line segment and circle intersect.

    :param Entity start: The start of the line segment. (Needs x, y attributes)
    :param Entity end: The end of the line segment. (Needs x, y attributes)
    :param Entity circle: The circle to test against. (Needs x, y, r attributes)
    :param float fudge: A fudge factor; additional distance to leave between the segment and circle. (Probably set this to the ship radius, 0.5.)
    :return: True if intersects, False otherwise
    :rtype: bool
    """
    # Derived with SymPy
    # Parameterize the segment as start + t * (end - start),
    # and substitute into the equation of a circle
    # Solve for t
    dx = end.x - start.x
    dy = end.y - start.y

    a = dx**2 + dy**2
    b = -2 * (start.x**2 - start.x*end.x - start.x*circle.x + end.x*circle.x +
              start.y**2 - start.y*end.y - start.y*circle.y + end.y*circle.y)
    c = (start.x - circle.x)**2 + (start.y - circle.y)**2

    if a == 0.0:
        # Start and end are the same point
        return calculate_distance_between(start, circle) <= circle.radius + fudge

    # Time along segment when closest to the circle (vertex of the quadratic)
    t = min(-b / (2 * a), 1.0)
    if t < 0:
        return False

    closest_x = start.x + dx * t
    closest_y = start.y + dy * t
    closest_distance = hlt.entity.Position(closest_x, closest_y).calculate_distance_between(circle)

    return closest_distance <= circle.radius + fudge


def _all_ships(game_map):
    all_ships = []
    for player in game_map.all_players():
        # if player == self.game_map.get_me():
        # continue
        all_ships.extend(player.all_ships())
    return all_ships


def almost_all_ships(game_map, ship_to_ignore, dispatch):
    all_ships = []
    for player in game_map.all_players():
        if player == game_map.get_me():
            continue
        all_ships.extend(player.all_ships())
    for ship in dispatch.ships:
        if ship == ship_to_ignore:
            continue
        all_ships.append(ship)
    return all_ships
