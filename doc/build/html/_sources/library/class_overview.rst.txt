==============
Class Overview
==============

The *Display Application* is consists of the following components:

* SerialCommunication
    * Handles the serial communication with the DGUS Display 
        * See :ref:`serial_communication`

* Display
    * Class that represents the Display

* Mask
    * A mask represents a Display Mask (Picture). It can contain multiple Controls

* Control
    * Is a base class that every control dervices from can be a Button, Data Display, Numeric Display, a.s.o



Diagram
=======

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

    class SerialCommunication {
    
    }

    Display -> SerialCommunication : Uses
    Mask -> SerialCommunication : Uses
    Control -> SerialCommunication : Uses

    Display "1" *-- "n" Mask : contains
    Mask "1" *-- "n" Control : contains

    Control <-- DataVariable : extends
    Control <-- TextVariable : extends

    