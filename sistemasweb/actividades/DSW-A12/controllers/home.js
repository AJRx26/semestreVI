const alumno = require("../models/alumno");

// home/index
const index = async function (req, res, next) {
	try {
		let items = await alumno.list()
		res.render("home", {
			model: items
		});
	} catch (err) {
		next(err);
	}
};

module.exports = { index };
