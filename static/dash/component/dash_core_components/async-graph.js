(window.webpackJsonpdash_core_components=window.webpackJsonpdash_core_components||[]).push([[3],{479:function(e,t,n){"use strict";(function(e){var n="object"==typeof e&&e&&e.Object===Object&&e;t.a=n}).call(this,n(223))},687:function(e,t,n){"use strict";n.r(t);var r=n(1),o=n.n(r),i=n(191),a=n(318),u=function(e){var t=[],n=null,r=function(){for(var r=arguments.length,o=new Array(r),i=0;i<r;i++)o[i]=arguments[i];t=o,n||(n=requestAnimationFrame((function(){n=null,e.apply(void 0,t)})))};return r.cancel=function(){n&&(cancelAnimationFrame(n),n=null)},r},c=n(0),l=n.n(c);var s=function(e){var t=typeof e;return null!=e&&("object"==t||"function"==t)},f=n(479),p="object"==typeof self&&self&&self.Object===Object&&self,d=f.a||p||Function("return this")(),h=function(){return d.Date.now()},y=d.Symbol,v=Object.prototype,b=v.hasOwnProperty,g=v.toString,m=y?y.toStringTag:void 0;var O=function(e){var t=b.call(e,m),n=e[m];try{e[m]=void 0;var r=!0}catch(e){}var o=g.call(e);return r&&(t?e[m]=n:delete e[m]),o},j=Object.prototype.toString;var _=function(e){return j.call(e)},w="[object Null]",P="[object Undefined]",k=y?y.toStringTag:void 0;var D=function(e){return null==e?void 0===e?P:w:k&&k in Object(e)?O(e):_(e)};var E=function(e){return null!=e&&"object"==typeof e},S="[object Symbol]";var T=function(e){return"symbol"==typeof e||E(e)&&D(e)==S},R=NaN,z=/^\s+|\s+$/g,C=/^[-+]0x[0-9a-f]+$/i,x=/^0b[01]+$/i,A=/^0o[0-7]+$/i,N=parseInt;var M=function(e){if("number"==typeof e)return e;if(T(e))return R;if(s(e)){var t="function"==typeof e.valueOf?e.valueOf():e;e=s(t)?t+"":t}if("string"!=typeof e)return 0===e?e:+e;e=e.replace(z,"");var n=x.test(e);return n||A.test(e)?N(e.slice(2),n?2:8):C.test(e)?R:+e},L="Expected a function",H=Math.max,F=Math.min;var W=function(e,t,n){var r,o,i,a,u,c,l=0,f=!1,p=!1,d=!0;if("function"!=typeof e)throw new TypeError(L);function y(t){var n=r,i=o;return r=o=void 0,l=t,a=e.apply(i,n)}function v(e){var n=e-c;return void 0===c||n>=t||n<0||p&&e-l>=i}function b(){var e=h();if(v(e))return g(e);u=setTimeout(b,function(e){var n=t-(e-c);return p?F(n,i-(e-l)):n}(e))}function g(e){return u=void 0,d&&r?y(e):(r=o=void 0,a)}function m(){var e=h(),n=v(e);if(r=arguments,o=this,c=e,n){if(void 0===u)return function(e){return l=e,u=setTimeout(b,t),f?y(e):a}(c);if(p)return clearTimeout(u),u=setTimeout(b,t),y(c)}return void 0===u&&(u=setTimeout(b,t)),a}return t=M(t)||0,s(n)&&(f=!!n.leading,i=(p="maxWait"in n)?H(M(n.maxWait)||0,t):i,d="trailing"in n?!!n.trailing:d),m.cancel=function(){void 0!==u&&clearTimeout(u),l=0,r=c=o=u=void 0},m.flush=function(){return void 0===u?a:g(h())},m},U="Expected a function";var G=function(e,t,n){var r=!0,o=!0;if("function"!=typeof e)throw new TypeError(U);return s(n)&&(r="leading"in n?!!n.leading:r,o="trailing"in n?!!n.trailing:o),W(e,t,{leading:r,maxWait:t,trailing:o})},q={debounce:W,throttle:G},J=function(e){return q[e]},$=function(e){return"function"==typeof e},B=function(){return"undefined"==typeof window},I=function(e){return e instanceof Element||e instanceof HTMLDocument};function V(e){return(V="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function K(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}function Q(e,t){return!t||"object"!==V(t)&&"function"!=typeof t?function(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}(e):t}function X(e){return(X=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}function Y(e,t){return(Y=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e})(e,t)}var Z=function(e){function t(){return function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,t),Q(this,X(t).apply(this,arguments))}var n,r,o;return function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&Y(e,t)}(t,e),n=t,(r=[{key:"render",value:function(){return this.props.children}}])&&K(n.prototype,r),o&&K(n,o),t}(r.PureComponent);function ee(e){return(ee="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function te(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}function ne(e){return(ne=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}function re(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}function oe(e,t){return(oe=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e})(e,t)}function ie(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}var ae=function(e){function t(e){var n;!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,t),n=function(e,t){return!t||"object"!==ee(t)&&"function"!=typeof t?re(e):t}(this,ne(t).call(this,e)),ie(re(n),"cancelHandler",(function(){n.resizeHandler&&n.resizeHandler.cancel&&(n.resizeHandler.cancel(),n.resizeHandler=null)})),ie(re(n),"rafClean",(function(){n.raf&&n.raf.cancel&&(n.raf.cancel(),n.raf=null)})),ie(re(n),"toggleObserver",(function(e){var t=n.getElement();t&&n.resizeObserver[e]&&n.resizeObserver[e](t)})),ie(re(n),"getElement",(function(){var e=n.props,t=e.querySelector,r=e.targetDomEl;if(!B()){if(t)return document.querySelector(t);if(r&&I(r))return r;var o=n.element&&Object(i.findDOMNode)(n.element);if(o)return o.parentElement}})),ie(re(n),"createUpdater",(function(){return n.rafClean(),n.raf=u((function(e){var t=e.width,r=e.height,o=n.props.onResize;$(o)&&o(t,r),n.setState({width:t,height:r})})),n.raf})),ie(re(n),"createResizeHandler",(function(e){var t=n.state,r=t.width,o=t.height,i=n.props,a=i.handleWidth,u=i.handleHeight;if(a||u){var c=n.createUpdater();e.forEach((function(e){var t=e&&e.contentRect||{},i=t.width,l=t.height,s=a&&r!==i||u&&o!==l;!n.skipOnMount&&s&&!B()&&c({width:i,height:l}),n.skipOnMount=!1}))}})),ie(re(n),"onRef",(function(e){n.element=e})),ie(re(n),"getRenderType",(function(){var e=n.props,t=e.render,o=e.children;return $(t)?"renderProp":$(o)?"childFunction":Object(r.isValidElement)(o)?"child":Array.isArray(o)?"childArray":"parent"})),ie(re(n),"getTargetComponent",(function(){var e=n.props,t=e.render,o=e.children,i=e.nodeType,a=n.state,u={width:a.width,height:a.height};switch(n.getRenderType()){case"renderProp":return Object(r.cloneElement)(t(u),{key:"resize-detector"});case"childFunction":return Object(r.cloneElement)(o(u));case"child":return Object(r.cloneElement)(o,u);case"childArray":return o.map((function(e){return!!e&&Object(r.cloneElement)(e,u)}));default:return Object(r.createElement)(i)}}));var o=e.skipOnMount,c=e.refreshMode,l=e.refreshRate,s=e.refreshOptions;n.state={width:void 0,height:void 0},n.skipOnMount=o,n.raf=null,n.element=null,n.unmounted=!1;var f=J(c);return n.resizeHandler=f?f(n.createResizeHandler,l,s):n.createResizeHandler,n.resizeObserver=new a.a(n.resizeHandler),n}var n,c,l;return function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&oe(e,t)}(t,e),n=t,(c=[{key:"componentDidMount",value:function(){this.toggleObserver("observe")}},{key:"componentWillUnmount",value:function(){this.toggleObserver("unobserve"),this.rafClean(),this.cancelHandler(),this.unmounted=!0}},{key:"render",value:function(){return o.a.createElement(Z,{ref:this.onRef},this.getTargetComponent())}}])&&te(n.prototype,c),l&&te(n,l),t}(r.PureComponent);ae.propTypes={handleWidth:c.bool,handleHeight:c.bool,skipOnMount:c.bool,refreshRate:c.number,refreshMode:c.string,refreshOptions:Object(c.shape)({leading:c.bool,trailing:c.bool}),querySelector:c.string,targetDomEl:c.any,onResize:c.func,render:c.func,children:c.any,nodeType:c.node},ae.defaultProps={handleWidth:!1,handleHeight:!1,skipOnMount:!1,refreshRate:1e3,refreshMode:void 0,refreshOptions:void 0,querySelector:null,targetDomEl:null,onResize:null,render:void 0,children:null,nodeType:"div"};var ue=ae,ce=n(193),le=n(21),se=n(165),fe=n(14),pe=n(194),de=n(691),he=n(192),ye=n(164),ve=n(23);function be(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{},r=Object.keys(n);"function"==typeof Object.getOwnPropertySymbols&&(r=r.concat(Object.getOwnPropertySymbols(n).filter((function(e){return Object.getOwnPropertyDescriptor(n,e).enumerable})))),r.forEach((function(t){ge(e,t,n[t])}))}return e}function ge(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function me(e,t){return function(e){if(Array.isArray(e))return e}(e)||function(e,t){var n=[],r=!0,o=!1,i=void 0;try{for(var a,u=e[Symbol.iterator]();!(r=(a=u.next()).done)&&(n.push(a.value),!t||n.length!==t);r=!0);}catch(e){o=!0,i=e}finally{try{r||null==u.return||u.return()}finally{if(o)throw i}}return n}(e,t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance")}()}function Oe(e){return(Oe="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function je(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}function _e(e){return(_e=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}function we(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}function Pe(e,t){return(Pe=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e})(e,t)}var ke={autosize:!0,height:void 0,width:void 0},De={},Ee={autosize:!1},Se={responsive:!0},Te={},Re={responsive:!1},ze=function(e,t,n){var r;if(Object(ce.a)(n,["click","hover","selected"])){var o=[];if(Object(le.a)(t))return null;for(var i=e.data,a=0;a<t.points.length;a++){var u=t.points[a],c=Object(se.a)((function(e){return!Object(ce.a)(Object(fe.a)(e),["Object","Array"])}),u);Object(pe.a)("curveNumber",u)&&Object(pe.a)("pointNumber",u)&&Object(pe.a)("customdata",i[c.curveNumber])&&(c.customdata=i[c.curveNumber].customdata[u.pointNumber]),Object(pe.a)("pointNumbers",u)&&(c.pointNumbers=u.pointNumbers),o[a]=c}r={points:o}}else"relayout"!==n&&"restyle"!==n||(r=t);return Object(pe.a)("range",t)&&(r.range=t.range),Object(pe.a)("lassoPoints",t)&&(r.lassoPoints=t.lassoPoints),r},Ce=function(e){function t(e){var n;return function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,t),(n=function(e,t){return!t||"object"!==Oe(t)&&"function"!=typeof t?we(e):t}(this,_e(t).call(this,e))).gd=o.a.createRef(),n._hasPlotted=!1,n._prevGd=null,n.bindEvents=n.bindEvents.bind(we(n)),n.getConfig=n.getConfig.bind(we(n)),n.getConfigOverride=n.getConfigOverride.bind(we(n)),n.getLayout=n.getLayout.bind(we(n)),n.getLayoutOverride=n.getLayoutOverride.bind(we(n)),n.graphResize=n.graphResize.bind(we(n)),n.isResponsive=n.isResponsive.bind(we(n)),n}var n,r,i;return function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&Pe(e,t)}(t,e),n=t,(r=[{key:"plot",value:function(e){var t=this,n=e.figure,r=e.config,o=e.animate,i=e.animation_options,a=e.responsive,u=this.gd.current;if(n=e._dashprivate_transformFigure(n,u),r=e._dashprivate_transformConfig(r,u),o&&this._hasPlotted&&n.data.length===u.data.length)return Plotly.animate(u,n,i);var c=this.getConfig(r,a),l=this.getLayout(n.layout,a);return u.classList.add("dash-graph--pending"),Plotly.react(u,{data:n.data,layout:l,frames:n.frames,config:c}).then((function(){var e=t.gd.current;e&&(e.classList.remove("dash-graph--pending"),t._hasPlotted&&e!==t._prevGd&&(t._prevGd&&t._prevGd.removeAllListeners&&(t._prevGd.removeAllListeners(),Plotly.purge(t._prevGd)),t._hasPlotted=!1),t._hasPlotted||(t.bindEvents(),t.graphResize(!0),t._hasPlotted=!0,t._prevGd=e))}))}},{key:"mergeTraces",value:function(e,t,n){var r=this,o=e.clearState;e[t].forEach((function(e){var t,o,i;if(Array.isArray(e)&&"object"===Oe(e[0])){var a=me(e,3);t=a[0],o=a[1],i=a[2]}else t=e;o||(o=function(e){return Array.from(Array(function(e){return e[Object.keys(e)[0]]}(e).length).keys())}(t));var u=r.gd.current;return Plotly[n](u,t,o,i)})),o(t)}},{key:"getConfig",value:function(e,t){return Object(de.a)(e,this.getConfigOverride(t))}},{key:"getLayout",value:function(e,t){return e?Object(de.a)(e,this.getLayoutOverride(t)):e}},{key:"getConfigOverride",value:function(e){switch(e){case!1:return Re;case!0:return Se;default:return Te}}},{key:"getLayoutOverride",value:function(e){switch(e){case!1:return Ee;case!0:return ke;default:return De}}},{key:"isResponsive",value:function(e){var t=e.config,n=e.figure,r=e.responsive;return"Boolean"===Object(fe.a)(r)?r:Boolean(t.responsive&&(!n.layout||(n.layout.autosize||Object(le.a)(n.layout.autosize))&&(Object(le.a)(n.layout.height)||Object(le.a)(n.layout.width))))}},{key:"graphResize",value:function(){var e=arguments.length>0&&void 0!==arguments[0]&&arguments[0];if(e||this.isResponsive(this.props)){var t=this.gd.current;t&&(t.classList.add("dash-graph--pending"),Plotly.Plots.resize(t).catch((function(){})).finally((function(){return t.classList.remove("dash-graph--pending")})))}}},{key:"bindEvents",value:function(){var e=this.props,t=e.setProps,n=e.clear_on_unhover,r=e.relayoutData,o=e.restyleData,i=e.hoverData,a=e.selectedData,u=this.gd.current;u.on("plotly_click",(function(e){var n=ze(u,e,"click");Object(le.a)(n)||t({clickData:n})})),u.on("plotly_clickannotation",(function(e){var n=Object(he.a)(["event","fullAnnotation"],e);t({clickAnnotationData:n})})),u.on("plotly_hover",(function(e){var n=ze(u,e,"hover");Object(le.a)(n)||Object(ye.a)(n,i)||t({hoverData:n})})),u.on("plotly_selected",(function(e){var n=ze(u,e,"selected");Object(le.a)(n)||Object(ye.a)(n,a)||t({selectedData:n})})),u.on("plotly_deselect",(function(){t({selectedData:null})})),u.on("plotly_relayout",(function(e){var n=ze(u,e,"relayout");Object(le.a)(n)||Object(ye.a)(n,r)||t({relayoutData:n})})),u.on("plotly_restyle",(function(e){var n=ze(u,e,"restyle");Object(le.a)(n)||Object(ye.a)(n,o)||t({restyleData:n})})),u.on("plotly_unhover",(function(){n&&t({hoverData:null})}))}},{key:"componentDidMount",value:function(){var e,t;this.plot(this.props),this.props.prependData&&this.mergeTraces(this.props,"prependData","prependTraces"),this.props.extendData&&this.mergeTraces(this.props,"extendData","extendTraces"),((null===(e=this.props.prependData)||void 0===e?void 0:e.length)||(null===(t=this.props.extendData)||void 0===t?void 0:t.length))&&this.props._dashprivate_onFigureModified(this.props.figure)}},{key:"componentWillUnmount",value:function(){var e=this.gd.current;e&&e.removeAllListeners&&(e.removeAllListeners(),this._hasPlotted&&Plotly.purge(e))}},{key:"shouldComponentUpdate",value:function(e){return this.props.id!==e.id||JSON.stringify(this.props.style)!==JSON.stringify(e.style)||JSON.stringify(this.props.loading_state)!==JSON.stringify(e.loading_state)}},{key:"UNSAFE_componentWillReceiveProps",value:function(e){var t,n;this.props.id!==e.id||(this.props.figure===e.figure&&this.props._dashprivate_transformConfig===e._dashprivate_transformConfig&&this.props._dashprivate_transformFigure===e._dashprivate_transformFigure||this.plot(e),this.props.prependData!==e.prependData&&this.mergeTraces(e,"prependData","prependTraces"),this.props.extendData!==e.extendData&&this.mergeTraces(e,"extendData","extendTraces"),((null===(t=this.props.prependData)||void 0===t?void 0:t.length)||(null===(n=this.props.extendData)||void 0===n?void 0:n.length))&&this.props._dashprivate_onFigureModified(this.props.figure))}},{key:"componentDidUpdate",value:function(e){e.id!==this.props.id&&this.plot(this.props)}},{key:"render",value:function(){var e=this.props,t=e.className,n=e.id,r=e.style,i=e.loading_state;return o.a.createElement("div",{id:n,key:n,"data-dash-is-loading":i&&i.is_loading||void 0,className:t,style:r},o.a.createElement(ue,{handleHeight:!0,handleWidth:!0,refreshMode:"debounce",refreshOptions:{trailing:!0},refreshRate:50,onResize:this.graphResize}),o.a.createElement("div",{ref:this.gd,style:{height:"100%",width:"100%"}}))}}])&&je(n.prototype,r),i&&je(n,i),t}(r.Component);Ce.propTypes=be({},ve.c,{prependData:l.a.arrayOf(l.a.oneOfType([l.a.array,l.a.object])),extendData:l.a.arrayOf(l.a.oneOfType([l.a.array,l.a.object])),clearState:l.a.func.isRequired}),Ce.defaultProps=be({},ve.b,{prependData:[],extendData:[]});t.default=Ce}}]);
//# sourceMappingURL=async-graph.js.map