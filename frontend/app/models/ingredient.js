import DS from 'ember-data';

export default DS.Model.extend({
    amount: DS.attr(),
    unit: DS.attr(),
    display_amount: DS.attr(),
    name: DS.attr(),
    category: DS.attr(),
    user: DS.attr(),
});
