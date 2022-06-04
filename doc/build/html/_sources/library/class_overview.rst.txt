==============
Class Overview
==============


Overview
========

.. uml::

    class Display {
    }

    class Mask {
    }

    abstract class Control {
    }

    class DataVariable {
    }

    class TextVariable {

    }

    Display "1" *-- "n" Mask : contains
    Mask "1" *-- "n" Control : contains

    Control <-- DataVariable : extends
    Control <-- TextVariable : extends