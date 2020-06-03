Vue.prototype.$db = wfpiDB;

Vue.component("contributor", {
  props: ["person"],
  template: "#contributor-template",
});

Vue.filter("formatDate", function (date) {
  let d = moment(date);
  return d.format("DD\xa0MMM\xa0YYYY");
});

Vue.filter("personImage", function (name) {
  return "assets/img/people/" + name.toLowerCase().replace(" ", "-") + ".jpg";
});

const podcastTable = new Vue({
  el: "#podcast-table",
  methods: {
    getNameAndBsn(person) {
      return person.name + ' ("' + person.bsn + '")';
    },
    getExperts: function (episode) {
      return episode.e
        .map((e) => this.getNameAndBsn(this.$db.experts[e]))
        .sort()
        .join("<br/>");
    },
    getPresenter: function (episode) {
      return this.getNameAndBsn(this.$db.presenters[episode.p]);
    },
    getRegions: function (episode) {
      return episode.e
        .map((e) => this.$db.experts[e].region)
        .sort()
        .join("<br/>");
    },
  },
});

const contributors = new Vue({
  el: "#contributors",
  computed: {
    // Essentially all active contributors minus Tim
    activeContributors: function () {
      let cs = Object.assign({}, this.$db.experts);
      // Remove Tim as he's in a section together with Dotun
      delete cs["rec3M8Ew2q6pTgV03"];

      let active = new Array();
      for (let [k, p] of Object.entries(cs)) {
        if (p.hasOwnProperty("active")) {
          active.push(p);
        }
      }

      return active.sort((a, b) => a.name.localeCompare(b.name));
    },

    // All inactive contributors + Seth Bennet
    pastContributors: function () {
      let cs = Object.assign({}, this.$db.experts);
      let active = new Array();
      for (let [k, p] of Object.entries(cs)) {
        if (!p.hasOwnProperty("active")) {
          active.push(p);
        }
      }

      active.push(this.$db.presenters["recXi10ToiF90unm7"]);

      return active.sort((a, b) => a.name.localeCompare(b.name));
    },
  },
});

const bsns = new Vue({
  el: "#bsnh",
  computed: {
    // Essentially all active contributors minus Tim
    getBSNHolders: function () {
      let active = new Array();
      for (let [k, p] of Object.entries(this.$db.bsnh)) {
        active.push(p);
      }

      return active.sort((a, b) => a.awardee.localeCompare(b.awardee));
    },
  },
});
