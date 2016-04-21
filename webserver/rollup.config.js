import babel from 'rollup-plugin-babel';
import commonjs from 'rollup-plugin-commonjs';
import nodeResolve from 'rollup-plugin-node-resolve';
import replace from 'rollup-plugin-replace';

export default {
  entry: 'static/js/main.js',
  sourceMap: true,
  plugins: [
    babel(),
    nodeResolve(),
    commonjs(),
    replace({'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)})
    ],
  dest: 'static/bundle.js'
};