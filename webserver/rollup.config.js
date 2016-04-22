import babel from 'rollup-plugin-babel';
import commonjs from 'rollup-plugin-commonjs';
import nodeResolve from 'rollup-plugin-node-resolve';
import replace from 'rollup-plugin-replace';

var useSourceMaps = true;

export default {
  entry: 'static/js/main.js',
  sourceMap: useSourceMaps,
  plugins: [
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
  dest: 'static/bundle.js',
  format: 'iife',
  exports: 'none'
};