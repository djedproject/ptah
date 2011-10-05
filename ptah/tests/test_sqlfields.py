import pyramid_sqla
import sqlalchemy as sqla
from memphis import config, form

from base import Base

SqlaBase = pyramid_sqla.get_base()
Session = pyramid_sqla.get_session()


class TestSqlSchema(Base):

    def test_sqlschema_fields(self):
        import ptah

        class Test(SqlaBase):
            __tablename__ = 'test'

            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode())
            count = sqla.Column(sqla.Integer())
            score = sqla.Column(sqla.Float())
            date = sqla.Column(sqla.Date())
            datetime = sqla.Column(sqla.DateTime())
            boolean = sqla.Column(sqla.Boolean())

        fieldset = ptah.generateFieldset(Test)

        # no primary keya
        self.assertNotIn('id', fieldset)

        self.assertEqual(fieldset['name'].__field__, 'text')
        self.assertEqual(fieldset['count'].__field__, 'int')
        self.assertEqual(fieldset['score'].__field__, 'float')
        self.assertEqual(fieldset['date'].__field__, 'date')
        self.assertEqual(fieldset['datetime'].__field__, 'datetime')
        self.assertEqual(fieldset['boolean'].__field__, 'bool')

        self.assertEqual(fieldset['name'].title, 'Name')


        fieldset = ptah.generateFieldset(Test, fieldNames=('name', 'count'))
        self.assertEqual(len(fieldset), 2)
        self.assertIn('name', fieldset)
        self.assertIn('count', fieldset)

        fieldset = ptah.generateFieldset(
            Test, fieldNames=('id', 'name'), skipPrimaryKey=False)
        self.assertEqual(len(fieldset), 2)
        self.assertIn('name', fieldset)
        self.assertIn('id', fieldset)
        self.assertTrue(fieldset['id'].readonly)

        # no table
        class TestNoTable(Test):
            pass

        self.assertIsNone(ptah.generateFieldset(TestNoTable))

    def test_sqlschema_extra_fields(self):
        import ptah

        class Test2(SqlaBase):
            __tablename__ = 'test2'

            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(
                sqla.Unicode(),
                info={'title': 'Test title',
                      'missing': 'missing value',
                      'description': 'Description',
                      'field_type': 'textarea',
                      'vocabulary': ['1','2']})

        fieldset = ptah.generateFieldset(Test2)

        field = fieldset['name']

        self.assertEqual(field.title, 'Test title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.missing, 'missing value')
        self.assertEqual(field.__field__, 'textarea')
        self.assertEqual(field.vocabulary, ['1', '2'])

    def test_sqlschema_custom(self):
        import ptah

        field = form.TextField('name', title = 'Custom')

        class Test3(SqlaBase):
            __tablename__ = 'test3'
            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode(), info={'field': field})

        fieldset = ptah.generateFieldset(Test3)

        m_field = fieldset['name']

        self.assertEqual(m_field.name, 'name')
        self.assertEqual(m_field.title, 'Custom')
        self.assertIs(m_field, field)

    def test_sqlschema_unknown(self):
        import ptah

        class Test2(SqlaBase):
            __tablename__ = 'test5'

            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode())
            json = sqla.Column(ptah.JsonListType())

        fieldset = ptah.generateFieldset(Test2)
        
        self.assertNotIn('json', fieldset)
