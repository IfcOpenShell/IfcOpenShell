import os
import pytest
import ifcopenshell
from ifcopenshell.util import mvd_info
from ifcopenshell.util.mvd_info import parse_mvd


@pytest.fixture
def load_fixture():
    base_dir = os.path.join(os.path.dirname(__file__), "fixtures", "mvd_parsing")
    def _load(filename):
        return ifcopenshell.open(os.path.join(base_dir, filename))
    return _load


class TestViewDefinition:
    def test_single_view(self, load_fixture):
        f = load_fixture("passing_header.ifc")
        assert f.mvd.view_definitions == ["Alignment-basedView"]

    def test_multiple_views(self, load_fixture):
        f = load_fixture("two_views.ifc")
        assert f.mvd.view_definitions == ['CoordinationView_V2.0', 'SpaceBoundaryAddonView']
        
    def test_add_view(self):
        header = MockHeader(("ViewDefinition [CoordinationView_V2.0]",))
        mvd = mvd_info.MvdInfo(header)
        assert mvd.view_definitions == ["CoordinationView_V2.0"]
        mvd.view_definitions.append("SpaceBoundaryAddonView")
        assert mvd.view_definitions == ['CoordinationView_V2.0', 'SpaceBoundaryAddonView']

class TestExchangeRequirements:
    def test_parsing(self, load_fixture):
        f = load_fixture("contains_exchange_requirement.ifc")
        parsed = parse_mvd(f.mvd.description)
        assert parsed.exchange_requirements == 'Any'

    def test_access_and_modification(self, load_fixture):
        f = load_fixture("contains_exchange_requirement.ifc")
        f.header.file_description.description = (
            'ViewDefinition [Alignment-basedView]',
            'ExchangeRequirement [SomethingElse]'
        )
        assert f.mvd.exchange_requirements == 'SomethingElse'
        f.mvd.view_definitions = ['CoordinationView_V2.0']
        assert f.mvd.view_definitions == ['CoordinationView_V2.0']


class TestComments:
    def test_read_and_append(self, load_fixture):
        f = load_fixture("contains_comment.ifc")
        assert f.mvd.comments == ['Any']
        f.mvd.comments = ['SomethingElse']
        assert f.mvd.comments == ['SomethingElse']
        f.mvd.comments.append('AnotherComment')
        assert f.mvd.comments == ['SomethingElse', ' AnotherComment']
        assert f.mvd.description[1] == 'Comment [SomethingElse, AnotherComment]'
    
    def test_comment_list_modifications(self, load_fixture):
        f = load_fixture("contains_comment.ifc")
        f.mvd.comments = ''
        f.mvd.comments.append('OnlyOne')
        assert 'OnlyOne' in f.mvd.comments
        
        f.mvd.comments.insert(0, 'FirstOne')
        f.mvd.comments[0] == 'FirstOne'

        f.mvd.comments.pop()
        assert f.mvd.comments[0] == 'FirstOne'
        
        del f.mvd.comments[0]
        assert not f.mvd.comments


class TestOptions:
    def test_string_options(self, load_fixture):
        f = load_fixture("contains_options.ifc")
        assert f.mvd.options == 'Any'
        assert 'options' in f.mvd.keywords


class TestDynamicFields:
    def test_options_modifications(self, load_fixture):
        f = load_fixture("dynamic_fields.ifc")

        f.mvd.options['ExcludedObjects'].append('Chair')
        f.mvd.options['SplitLevel'] = 'Off'
        f.mvd.options['OtherAttr'] = 'SomeValue'

        assert f.mvd.description[2].startswith('Option [')
        assert 'OtherAttr: SomeValue' in f.mvd.description[2]
        assert f.mvd.description == f.header.file_description.description

    def test_remark_editing(self, load_fixture):
        f = load_fixture("dynamic_fields.ifc")
        assert f.mvd.remark == {'SomeKey': 'SomeValue', 'AnotherKey': 'AnotherValue'}
        f.mvd.remark['AnotherKey'] = 'SometingElse'
        f.mvd.remark['IncludedObjects'] = ['Floor', 'Roof']
        assert f.mvd.remark['AnotherKey'] == 'SometingElse'
        assert f.mvd.remark['IncludedObjects'] == ['Floor', 'Roof']
        assert 'remark' in f.mvd.keywords
    
    def test_custom_dict_behavior(self, load_fixture):
        f = load_fixture("dynamic_fields.ifc")
        
        # delete
        del f.mvd.options['SplitLevel']
        assert not f.mvd.options.get('SplitLevel')
        
        # keys, values, items 
        assert set(f.mvd.remark.keys()) == {'SomeKey', 'AnotherKey'}
        assert 'SomeValue' in f.mvd.remark.values()
        assert ('SomeKey', 'SomeValue') in f.mvd.remark.items()
        
        # containment
        assert 'SomeKey' in f.mvd.remark
        assert 'MissingKey' not in f.mvd.remark


class TestKeywords:
    @pytest.mark.parametrize("filename, expected_keywords", [
        ("contains_comment.ifc", {"view_definitions", "comments"}),
        ("contains_exchange_requirement.ifc", {"view_definitions", "exchange_requirements"}),
        ("contains_options.ifc", {"view_definitions", "options"}),
        ("dynamic_fields.ifc", {"view_definitions", "exchange_requirements", "comments", "remark"})
    ])
    def test_keywords_present(self, load_fixture, filename, expected_keywords):
        f = load_fixture(filename)
        assert f.mvd.keywords == expected_keywords


class TestFallbackBehavior:
    def test_parse_mvd_fallback(self, monkeypatch):
        monkeypatch.setattr(mvd_info, "LARK_AVAILABLE", False)
        header = MockHeader(("ViewDefinition [ShouldNotParse]",))
        mvd = mvd_info.MvdInfo(
            header
        )
        assert mvd.view_definitions is None
        assert mvd.keywords == set()
        
class MockHeader:
    def __init__(self, description):
        self.file_description = type("FileDescription", (), {"description": description})

