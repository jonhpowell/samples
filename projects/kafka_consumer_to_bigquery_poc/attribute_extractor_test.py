
import unittest
import attribute_extractor


class AttributeExtractorTest(unittest.TestCase):

    def test_decompose_comcast_attrs(self):
        check_str = 'neutron_ovs_agent_check--oscomp-as-c152'

        (tenant, env, node, check) = attribute_extractor.extract_attributes('pistore-as-d123.ece.someco.net', check_str)
        self.assertEqual(env, 'as-d', "simple environment")
        self.assertEqual(node, 'pistore123', "3-digit node")

        (tenant, env, node, check) = attribute_extractor.extract_attributes('pistore-as-d45.ece.someco.net', check_str)
        self.assertEqual(env, 'as-d', "simple environment")
        self.assertEqual(node, 'pistore45', "2-digit node")

        (tenant, env, node, check) = attribute_extractor.extract_attributes('pistore-as-d6.ece.someco.net', check_str)
        self.assertEqual(env, 'as-d', "simple environment")
        self.assertEqual(node, 'pistore6', "1-digit node")

    def test_decompose_more_complex(self):
        check_str = 'neutron_ovs_agent_check--oscomp-as-c152'

        (tenant, env, node, check) = attribute_extractor.extract_attributes('oscomp-ch2-h117.ece.someco.net', check_str)
        self.assertEqual(env, 'ch2-h', "more complex environment")
        self.assertEqual(node, 'oscomp117', "3-digit node, complex env")

        (tenant, env, node, check) = attribute_extractor.extract_attributes('oscomp-ch2-h117.ece.someco.net', check_str)
        self.assertEqual(env, 'ch2-h', "more complex environment")
        self.assertEqual(node, 'oscomp117', "3-digit node, complex env")

        (tenant, env, node, check) = attribute_extractor.extract_attributes('914114-infra02.ord1.hpe-flexcap.com', check_str)
        self.assertEqual(env, 'infra02', "non-comcast ex array lim check")
        self.assertEqual(node, '914114', "non-comcast")

        (tenant, env, node, check) = attribute_extractor.extract_attributes('osctrl-as-d01.ece.someco.net', 'rabbitmq_status--osctrl-as-d01_rabbit_mq_container-e74a1936')
        self.assertEqual(tenant, 'ece.someco.net', "tenant")
        self.assertEqual(env, 'as-d', "environ")
        self.assertEqual(node, 'osctrl01', "node")
        self.assertEqual(check, 'rabbitmq_status', "check")


if __name__ == '__main__':
    unittest.main()

