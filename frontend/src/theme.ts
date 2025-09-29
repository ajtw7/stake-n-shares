import { extendTheme } from "@chakra-ui/react";

const theme = extendTheme({
  styles: {
    global: {
      "html, body, #root": {
        height: "100%",
        background: "#ffffff",
        color: "#000000",
        margin: 0,
        fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial",
      },
    },
  },
  colors: {
    brand: {
      50: "#ffffff",
      100: "#f8f8f8",
      900: "#000000"
    }
  },
  components: {
    Button: {
      baseStyle: { borderRadius: "8px" }
    }
  }
});

export default theme;