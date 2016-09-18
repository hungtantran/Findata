import babel from 'rollup-plugin-babel';
import commonjs from 'rollup-plugin-commonjs';
import nodeResolve from 'rollup-plugin-node-resolve';
import replace from 'rollup-plugin-replace';
import json from 'rollup-plugin-json';

var useSourceMaps = true;

export default {
  entry: 'js/login.js',
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
        sourceMap: useSourceMaps
    }),
    replace({
        'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
        sourceMap: useSourceMaps
    })
    ],
  dest: 'static/generated/login.js',
  format: 'iife',
  exports: 'none'
};