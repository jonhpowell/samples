
class ProcessString(object):

    def decompose_comcast_attrs(self, entity_label, check_label):
        first_per_idx = entity_label.find('.')
        first_dash_idx = entity_label.find('-')
        first_ddash_idx = check_label.find("--")
        attr0 = entity_label[first_per_idx + 1:]
        attr1 = entity_label[first_dash_idx + 1:first_dash_idx+5]
        attr2 = entity_label[:first_dash_idx] + entity_label[first_dash_idx+5:first_per_idx]
        attr3 = check_label[:first_ddash_idx]
        return attr0, attr1, attr2, attr3

#        print("attrs0='{0}' attrs1='{1}' attrs2='{2}' attrs3='{3}' ('{4}')".format(attr0, attr1, attr2, attr3, str_in))


if __name__ == '__main__':

    str0 = 'pistore-as-d123.ece.someco.net'
    str1 = 'pistore-as-d45.ece.someco.net'
    str2 = 'pistore-as-d6.ece.someco.net'
    str3 = 'oscomp-ch2-h117.ece.someco.net'
    check_str = 'neutron_ovs_agent_check--oscomp-as-c152'
    ps = ProcessString()
    print(ps.decompose_comcast_attrs(str0, check_str))
    print(ps.decompose_comcast_attrs(str1, check_str))
    print(ps.decompose_comcast_attrs(str2, ''))
