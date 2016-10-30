import babel from 'rollup-plugin-babel';
import commonjs from 'rollup-plugin-commonjs';
import nodeResolve from 'rollup-plugin-node-resolve';
import replace from 'rollup-plugin-replace';
import json from 'rollup-plugin-json';

var useSourceMaps = true;

export default {
  entry: 'js/app.js',
  sourceMap: useSourceMaps,
  plugins: [
    json({
        sourceMap: useSourceMaps,
        include: 'models/**'
    }),
    babel({
        exclude: 'node_modules/**',
        sourceMaps: useSourceMaps,
        sourceMap: useSourceMaps
    }),
    nodeResolve({
        jsnext: true,
        main: true
    }),
    commonjs({
        include: 'node_modules/**',
        sourceMap: useSourceMaps,
        namedExports: {
            'node_modules/react/react.js': ['PropTypes', 'createElement'],
        }
    }),
    replace({
        'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
        sourceMap: useSourceMaps
    })
    ],
  dest: 'static/generated/app.js',
  format: 'iife',
  exports: 'none'
};