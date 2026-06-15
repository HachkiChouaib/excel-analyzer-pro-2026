"""Presentation layer: one module per application screen.

Each ``render()`` function reads the active DataFrame from ``st.session_state``
and delegates all computation to the :mod:`utils` package.
"""
