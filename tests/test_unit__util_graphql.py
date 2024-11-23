from gpt_multi_atomic_agents import util_graphql
from parameterized import parameterized
import unittest

from rich.console import Console

console = Console()


class TestUtil_Graphql(unittest.TestCase):
    @parameterized.expand(
        [
            (
                "test: Parse mutations from schema.",
                [
                    """
type Mutation {
  addCreature(input: CreatureInput!): Creature!
}

input CreatureInput {
  creature_name: String!
  allowed_terrain: TerrainType!
  age: Int!
  icon_name: IconType!
}
""",
                    """
type Mutation {
  addVegetation(input: VegetationInput!): Vegetation!
}

input VegetationInput {
  vegetation_name: String!
  icon_name: IconType!
  allowed_terrain: TerrainType!
}
""",
                    """
type Mutation {
  addCreatureRelationship(input: RelationshipInput!): Relationship!
}

input RelationshipInput {
  from_name: String!
  to_name: String!
  relationship_kind: RelationshipType!
}
""",
                ],
                ["addCreature", "addVegetation", "addCreatureRelationship"],
            ),
            (
                "test: Parse mutations from multiple schemas.",
                [
                    """type Query {\n  creatures: [Creature!]!\n  vegetations: [Vegetation!]!\n  relationships: [Relationship!]!\n}\n\ntype Creature {\n  id: ID!\n  creature_name: String!\n  allowed_terrain: TerrainType!\n  age: Int!\n  icon_name: IconType!\n}\n\ntype Vegetation {\n  id: ID!\n        
vegetation_name: String!\n  icon_name: IconType!\n  allowed_terrain: TerrainType!\n}\n\ntype Relationship {\n  id: ID!\n  from_name: String!\n  to_name: String!\n  relationship_kind: RelationshipType!\n}\n\nenum TerrainType {\n  MOUNTAIN\n  MARSH\n  PRAIRIE\n  COAST\n
WATER\n}\n\nenum IconType {\n  SHEEP_ICON\n  WOLF_ICON\n  GRASS_ICON\n  HUMAN_ICON\n  OTHER_ICON\n}\n\nenum RelationshipType {\n  EATS\n  BUYS\n  FEEDS\n  SELLS\n}\n', 'type Mutation {\n  addCreature(input: CreatureInput!): Creature!\n}\n\ninput CreatureInput {\n  creature_name:  
String!\n  allowed_terrain: TerrainType!\n  age: Int!\n  icon_name: IconType!\n}\n""",
                    """type Mutation {\n  addVegetation(input: VegetationInput!): Vegetation!\n}\n\ninput VegetationInput {\n  vegetation_name: String!\n  icon_name: IconType!\n  allowed_terrain: TerrainType!\n}\n""",
                    """type Mutation {\n  addCreatureRelationship(input: RelationshipInput!): Relationship!\n}\n\ninput RelationshipInput {\n  from_name: String!\n  to_name: String!\n  relationship_kind: RelationshipType!\n}\n""",
                ],
                ["addCreature", "addVegetation", "addCreatureRelationship"],
            ),
        ]
    )
    def test_parse_out_mutations(
        self,
        _test_name_implicitly_used: str,
        accepted_graphql_schemas: list[str],
        expected_mutation_names,
    ) -> None:
        actual = util_graphql.parse_out_mutation_names_from_schemas(
            accepted_graphql_schemas=accepted_graphql_schemas
        )
        self.assertEqual(
            expected_mutation_names,
            actual,
            "Parsed out mutation names are not as expected",
        )

    @parameterized.expand(
        [
            (
                "test: Filter 3 mutation calls.",
                [
                    """mutation {\n    addCreature(input: {\n      creature_name: "sheep",\n      allowed_terrain: GRASSLAND,\n      age: 2,\n      icon_name: SHEEP\n    }) {\n      creature_name\n      allowed_terrain\n      age\n      icon_name\n    }""",
                    """mutation {', '  addVegetation(input: {', '    vegetation_name: "Grass",', '    icon_name: GRASS,', '    allowed_terrain: LAND', '  }) {', '    vegetation_name', '    icon_name', '    allowed_terrain', '  }', '}'""",
                    """mutation {', '  addCreatureRelationship(input: {', '    from_name: "Sheep",', '    to_name: "Grass",', '    relationship_kind: EATS', '  }) {', '    id', '  }', '}'""",
                ],
                ["addCreature"],
                [
                    """mutation {\n    addCreature(input: {\n      creature_name: "sheep",\n      allowed_terrain: GRASSLAND,\n      age: 2,\n      icon_name: SHEEP\n    }) {\n      creature_name\n      allowed_terrain\n      age\n      icon_name\n    }""",
                ],
            ),
            (
                "test: Filter more complicated calls",
                [
                    """mutation {\n    addCreature(input: {\n      creature_name: "Xenomorph"\n      allowed_terrain: SPACE\n      age: 1\n      icon_name: ALIEN\n    }) {\n      creature_name\n    }\n  }""",
                    """mutation {\n    addCreature(input: {\n      creature_name: "Ellen Ripley"\nallowed_terrain: SPACE\n      age: 30\n      icon_name: HUMAN\n    }) {\n      creature_name\n    }\n  }""",
                    """mutation {\n    addCreature(input: {\n      creature_name: "Dallas"\n      allowed_terrain: SPACE\n      age: 35\n      icon_name: HUMAN\n    }) {\n      creature_name\n    }\n  }""",
                    """mutation {\n    addCreature(input: {\n      creature_name: "Kane"\n      allowed_terrain: SPACE\n      age: 33\n      icon_name: HUMAN\n    }) {\n      creature_name\n    }\n  }""",
                    """mutation {\n    addVegetation(input: {\n      vegetation_name: "Space Fern",\nicon_name: PLANT,\n      allowed_terrain: FOREST\n    }) {\n      id\n    }\n  }""",
                    """mutation {\n    addVegetation(input: {\n      vegetation_name: "Xenomorph Fungus",\n      icon_name: MUSHROOM,\n      allowed_terrain: CAVE\n    }) {\n      id\n    }\n  }""",
                    """mutation {\n addVegetation(input: {\n      vegetation_name: "Acid-Resistant Moss",\n      icon_name: GRASS,\n      allowed_terrain: ROCKY\n    }) {\n      id\n    }\n  }""",
                    """mutation {\n    addVegetation(input: {\n      vegetation_name: "Bioluminescent Vines",\n      icon_name: VINE,\n allowed_terrain: JUNGLE\n    }) {\n      id\n    }\n  }""",
                ],
                ["addVegetation"],
                [
                    """mutation {\n    addVegetation(input: {\n      vegetation_name: "Space Fern",\nicon_name: PLANT,\n      allowed_terrain: FOREST\n    }) {\n      id\n    }\n  }""",
                    """mutation {\n    addVegetation(input: {\n      vegetation_name: "Xenomorph Fungus",\n      icon_name: MUSHROOM,\n      allowed_terrain: CAVE\n    }) {\n      id\n    }\n  }""",
                    """mutation {\n addVegetation(input: {\n      vegetation_name: "Acid-Resistant Moss",\n      icon_name: GRASS,\n      allowed_terrain: ROCKY\n    }) {\n      id\n    }\n  }""",
                    """mutation {\n    addVegetation(input: {\n      vegetation_name: "Bioluminescent Vines",\n      icon_name: VINE,\n allowed_terrain: JUNGLE\n    }) {\n      id\n    }\n  }""",
                ],
            ),
        ]
    )
    def test_filter_to_matching_mutations_calls(
        self,
        _test_name_implicitly_used: str,
        previously_generated_mutation_calls: list[str],
        accepted_mutation_names: list[str],
        expected_mutations: str,
    ):
        actual_mutations = util_graphql.filter_to_matching_mutation_calls(
            previously_generated_mutation_calls=previously_generated_mutation_calls,
            accepted_mutation_names=accepted_mutation_names,
        )
        self.assertEqual(
            expected_mutations,
            actual_mutations,
            "Filtered mutation names are not as expected",
        )
