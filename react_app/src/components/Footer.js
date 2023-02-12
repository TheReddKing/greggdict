import React from "react";

import { version } from "../settings";

const Footer = () => (
  <div className="mt-8 mb-6 sm:mt-12 sm:mb-8 text-center text-gray-600">
    <a href="https://github.com/thereddking/greggdict/releases">{version}</a> |
    &copy; Kevin Fang 2022, forked from{" "}
    <a href="https://github.com/richyliu/greggdict">Richard Liu</a>
  </div>
);

export default Footer;
